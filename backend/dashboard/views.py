# dashboard/views.py
from __future__ import annotations

from datetime import date

from django.db.models import (
    Count, Sum, F, Q, Value, IntegerField, DecimalField, ExpressionWrapper,
    OuterRef, Subquery
)
from django.db.models.functions import Coalesce, TruncDay, Cast
from django.utils.dateparse import parse_date

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from vente.models import Commande, LigneCommande
from encaissement.models import Encaissement
from charge.models import Charge
from achats.models import Achat, AchatLigne


# -----------------------------
# Helpers dates / base queryset
# -----------------------------
def _parse_dates(request):
    dfrom = parse_date((request.query_params.get("date_from") or "").strip())
    dto = parse_date((request.query_params.get("date_to") or "").strip())

    today = date.today()
    if not dfrom:
        dfrom = today.replace(day=1)
    if not dto:
        dto = today

    return dfrom, dto


def _base_qs(request):
    dfrom, dto = _parse_dates(request)
    qs = (
        Commande.objects
        .select_related("page", "frais_livraison", "encaissement")
        .filter(created_at__date__gte=dfrom, created_at__date__lte=dto)
    )

    page_id = (request.query_params.get("page") or "").strip()
    if page_id.isdigit():
        qs = qs.filter(page_id=int(page_id))

    return qs, dfrom, dto


# -----------------------------
# Expressions CA / frais / charges
# -----------------------------
def _ca_expr():
    """
    CA articles = SUM(qte * prix_vente_unitaire) via lignes
    """
    return Coalesce(
        Sum(
            ExpressionWrapper(
                F("lignes__quantite") * F("lignes__prix_vente_unitaire"),
                output_field=DecimalField(max_digits=18, decimal_places=2),
            )
        ),
        Value(0, output_field=DecimalField(max_digits=18, decimal_places=2)),
    )


def _frais_expr():
    return Coalesce(
        Sum(Cast(F("frais_livraison__frais_final"), IntegerField())),
        Value(0, output_field=IntegerField()),
    )


def _charges_paid_sum_expr():
    return Coalesce(
        Sum(
            Cast(F("charges__montant"), DecimalField(max_digits=18, decimal_places=2)),
            filter=Q(charges__statut="PAYEE"),
        ),
        Value(0, output_field=DecimalField(max_digits=18, decimal_places=2)),
    )


# -----------------------------
# COGS / dépenses / subquery coût achat
# -----------------------------
def _latest_purchase_price_subquery():
    """
    Dernier prix d'achat connu pour un article.
    (On prend le plus récent AchatLigne via achat.date_achat sinon achat.created_at)
    """
    al_qs = (
        AchatLigne.objects
        .filter(article_id=OuterRef("article_id"))
        .select_related("achat")
        .order_by(
            F("achat__date_achat").desc(nulls_last=True),
            F("achat__created_at").desc(nulls_last=True),
            F("created_at").desc(nulls_last=True),
            "-id",
        )
        .values("prix_achat_unitaire")[:1]
    )
    return Subquery(al_qs, output_field=DecimalField(max_digits=12, decimal_places=2))


def _cogs_total_for_commandes(qs_commandes):
    """
    Coût estimé des articles vendus (COGS) sur la période
    = SUM(qte_vendue * dernier_prix_achat_connu(article))
    """
    base = (
        LigneCommande.objects
        .select_related("commande", "article")
        .filter(commande__in=qs_commandes.exclude(statut=Commande.Statut.ANNULEE))
    )

    latest_cost = _latest_purchase_price_subquery()

    agg = (
        base.annotate(
            cout_unit=Coalesce(
                latest_cost,
                Value(0, output_field=DecimalField(max_digits=12, decimal_places=2))
            ),
            cout_ligne=ExpressionWrapper(
                F("quantite") * F("cout_unit"),
                output_field=DecimalField(max_digits=18, decimal_places=2),
            ),
        )
        .aggregate(
            cogs=Coalesce(
                Sum("cout_ligne"),
                Value(0, output_field=DecimalField(max_digits=18, decimal_places=2))
            )
        )
    )

    return agg["cogs"] or 0


def _achats_total_in_range(dfrom: date, dto: date):
    """
    Total achats sur période = SUM(qte * prix_achat_unitaire)
    """
    achats_qs = Achat.objects.filter(
        Q(date_achat__gte=dfrom, date_achat__lte=dto) |
        Q(date_achat__isnull=True, created_at__date__gte=dfrom, created_at__date__lte=dto)
    )

    agg = AchatLigne.objects.filter(achat__in=achats_qs).aggregate(
        total=Coalesce(
            Sum(
                ExpressionWrapper(
                    F("quantite") * F("prix_achat_unitaire"),
                    output_field=DecimalField(max_digits=18, decimal_places=2),
                )
            ),
            Value(0, output_field=DecimalField(max_digits=18, decimal_places=2)),
        )
    )
    return agg["total"] or 0


def _charges_total_in_range(dfrom: date, dto: date):
    agg = Charge.objects.filter(
        statut="PAYEE",
        date_charge__gte=dfrom,
        date_charge__lte=dto,
    ).aggregate(
        total=Coalesce(
            Sum("montant"),
            Value(0, output_field=DecimalField(max_digits=18, decimal_places=2))
        )
    )
    return agg["total"] or 0


# -----------------------------
# Views Dashboard
# -----------------------------
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def dashboard_overview(request):
    qs, dfrom, dto = _base_qs(request)

    ca_articles = _ca_expr()
    ca_frais = _frais_expr()

    agg_all = qs.aggregate(
        nb=Count("id"),
        nb_livrees=Count("id", filter=Q(statut=Commande.Statut.LIVREE)),
        nb_annulees=Count("id", filter=Q(statut=Commande.Statut.ANNULEE)),
        ca_articles=ca_articles,
        ca_frais=ca_frais,
    )

    ca_total_commandes = int(float(agg_all["ca_articles"] or 0)) + int(agg_all["ca_frais"] or 0)
    nb = int(agg_all["nb"] or 0)
    panier_moyen = int(ca_total_commandes / nb) if nb else 0

    qs_paid = qs.filter(encaissement__statut=Encaissement.StatutPaiement.PAYEE)
    agg_paid = qs_paid.aggregate(
        nb=Count("id"),
        ca_articles=ca_articles,
        ca_frais=ca_frais,
    )

    ca_total_encaisse = int(float(agg_paid["ca_articles"] or 0)) + int(agg_paid["ca_frais"] or 0)
    nb_paid = int(agg_paid["nb"] or 0)
    panier_moyen_encaisse = int(ca_total_encaisse / nb_paid) if nb_paid else 0

    charges_total = _charges_total_in_range(dfrom, dto)
    achats_total = _achats_total_in_range(dfrom, dto)
    depenses_total = (charges_total or 0) + (achats_total or 0)

    cogs = _cogs_total_for_commandes(qs)
    benefice_estime = float(ca_total_commandes) - float(cogs or 0) - float(charges_total or 0)

    return Response({
        "range": {"date_from": dfrom.isoformat(), "date_to": dto.isoformat()},

        "nb_commandes": nb,
        "nb_livrees": int(agg_all["nb_livrees"] or 0),
        "nb_annulees": int(agg_all["nb_annulees"] or 0),

        "ca_total_commandes": ca_total_commandes,
        "ca_total_encaisse": ca_total_encaisse,
        "panier_moyen": panier_moyen,
        "panier_moyen_encaisse": panier_moyen_encaisse,

        "charges_total": int(float(charges_total or 0)),
        "achats_total": int(float(achats_total or 0)),
        "depenses_total": int(float(depenses_total or 0)),
        "cogs_estime": int(float(cogs or 0)),
        "benefice_estime": int(float(benefice_estime or 0)),
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def dashboard_ca_by_day(request):
    qs, dfrom, dto = _base_qs(request)
    ca_articles = _ca_expr()

    rows = (
        qs.annotate(day=TruncDay("created_at"))
        .values("day")
        .annotate(
            ca_articles=ca_articles,
            frais=Coalesce(Sum(Cast(F("frais_livraison__frais_final"), IntegerField())), Value(0)),
            nb=Count("id"),
        )
        .order_by("day")
    )

    points = []
    for r in rows:
        ca = int(float(r["ca_articles"] or 0)) + int(r["frais"] or 0)
        points.append({"x": r["day"].date().isoformat(), "y": ca})

    return Response({
        "range": {"date_from": dfrom.isoformat(), "date_to": dto.isoformat()},
        "label": "CA (commandes)",
        "points": points,
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def dashboard_commandes_by_statut(request):
    qs, dfrom, dto = _base_qs(request)
    rows = qs.values("statut").annotate(nb=Count("id")).order_by("statut")

    return Response({
        "range": {"date_from": dfrom.isoformat(), "date_to": dto.isoformat()},
        "items": [{"statut": r["statut"], "nb": int(r["nb"] or 0)} for r in rows],
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def dashboard_top_articles(request):
    qs, dfrom, dto = _base_qs(request)
    qs = qs.exclude(statut=Commande.Statut.ANNULEE)

    rows = (
        LigneCommande.objects
        .select_related("article", "commande")
        .filter(commande__in=qs)
        .values("article_id", "article__reference", "article__nom_produit")
        .annotate(
            qte_total=Coalesce(Sum("quantite"), Value(0)),
            ca=Coalesce(
                Sum(
                    ExpressionWrapper(
                        F("quantite") * F("prix_vente_unitaire"),
                        output_field=DecimalField(max_digits=18, decimal_places=2),
                    )
                ),
                Value(0, output_field=DecimalField(max_digits=18, decimal_places=2)),
            ),
        )
        .order_by("-ca")
    )

    limit = (request.query_params.get("limit") or "").strip()
    rows = rows[: int(limit)] if limit.isdigit() else rows[:10]

    items = []
    for r in rows:
        items.append({
            "article_id": int(r["article_id"]),
            "reference": r["article__reference"] or "",
            "nom_produit": r["article__nom_produit"] or "",
            "quantite": int(r["qte_total"] or 0),
            "ca": int(float(r["ca"] or 0)),
        })

    return Response({
        "range": {"date_from": dfrom.isoformat(), "date_to": dto.isoformat()},
        "items": items,
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def dashboard_payment_mix(request):
    qs, dfrom, dto = _base_qs(request)
    paid = qs.filter(encaissement__statut=Encaissement.StatutPaiement.PAYEE)

    rows = (
        paid.values("encaissement__mode")
        .annotate(
            nb=Count("id"),
            ca_articles=_ca_expr(),
            frais=Coalesce(Sum(Cast(F("frais_livraison__frais_final"), IntegerField())), Value(0)),
        )
        .order_by("encaissement__mode")
    )

    items = []
    for r in rows:
        ca = int(float(r["ca_articles"] or 0)) + int(r["frais"] or 0)
        items.append({"mode": r["encaissement__mode"] or "", "nb": int(r["nb"] or 0), "ca": ca})

    return Response({
        "range": {"date_from": dfrom.isoformat(), "date_to": dto.isoformat()},
        "items": items,
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def dashboard_sales_by_page(request):
    qs, dfrom, dto = _base_qs(request)

    rows = (
        qs.values("page_id", "page__nom")
        .annotate(
            nb=Count("id"),
            ca_articles=_ca_expr(),
            frais=Coalesce(Sum(Cast(F("frais_livraison__frais_final"), IntegerField())), Value(0)),
        )
        .order_by("-nb")
    )

    items = []
    for r in rows:
        ca = int(float(r["ca_articles"] or 0)) + int(r["frais"] or 0)
        items.append({
            "page_id": r["page_id"],
            "page_nom": r["page__nom"],
            "nb": int(r["nb"] or 0),
            "ca": ca,
        })

    return Response({
        "range": {"date_from": dfrom.isoformat(), "date_to": dto.isoformat()},
        "items": items,
    })


# -----------------------------
# ✅ Articles sortants (ventes) - FIX: qte_total au lieu de quantite
# -----------------------------
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def dashboard_articles_sortants(request):
    qs, dfrom, dto = _base_qs(request)
    qs = qs.exclude(statut=Commande.Statut.ANNULEE)

    latest_cost = _latest_purchase_price_subquery()

    rows = (
        LigneCommande.objects
        .select_related("article", "commande")
        .filter(commande__in=qs)
        .values("article_id", "article__reference", "article__nom_produit")
        .annotate(
            qte_total=Coalesce(Sum("quantite"), Value(0)),
            total_vente=Coalesce(
                Sum(
                    ExpressionWrapper(
                        F("quantite") * F("prix_vente_unitaire"),
                        output_field=DecimalField(max_digits=18, decimal_places=2),
                    )
                ),
                Value(0, output_field=DecimalField(max_digits=18, decimal_places=2)),
            ),
            cout_unit=Coalesce(
                latest_cost,
                Value(0, output_field=DecimalField(max_digits=12, decimal_places=2))
            ),
        )
        .order_by("-total_vente")
    )

    items = []
    for r in rows:
        qte = int(r["qte_total"] or 0)
        total_vente = float(r["total_vente"] or 0)
        cout_unit = float(r["cout_unit"] or 0)

        prix_moyen_vente = int(total_vente / qte) if qte else 0
        cout_total = qte * cout_unit
        marge = total_vente - cout_total

        items.append({
            "article_id": int(r["article_id"]),
            "reference": r["article__reference"] or "",
            "nom_produit": r["article__nom_produit"] or "",
            "quantite": qte,  # ✅ output attendu par le frontend/serializer
            "prix_moyen_vente": int(prix_moyen_vente),
            "total_vente": int(total_vente),
            "cout_unit_estime": int(cout_unit),
            "cout_total_estime": int(cout_total),
            "marge_estime": int(marge),
        })

    limit = (request.query_params.get("limit") or "").strip()
    if limit.isdigit():
        items = items[: int(limit)]

    return Response({
        "range": {"date_from": dfrom.isoformat(), "date_to": dto.isoformat()},
        "items": items,
    })


# -----------------------------
# ✅ Articles entrants (achats) - FIX: qte_total au lieu de quantite
# -----------------------------
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def dashboard_articles_entrants(request):
    dfrom, dto = _parse_dates(request)

    achats_qs = Achat.objects.filter(
        Q(date_achat__gte=dfrom, date_achat__lte=dto) |
        Q(date_achat__isnull=True, created_at__date__gte=dfrom, created_at__date__lte=dto)
    )

    rows = (
        AchatLigne.objects
        .select_related("article", "achat")
        .filter(achat__in=achats_qs)
        .values("article_id", "article__reference", "article__nom_produit")
        .annotate(
            qte_total=Coalesce(Sum("quantite"), Value(0)),
            total_achat=Coalesce(
                Sum(
                    ExpressionWrapper(
                        F("quantite") * F("prix_achat_unitaire"),
                        output_field=DecimalField(max_digits=18, decimal_places=2),
                    )
                ),
                Value(0, output_field=DecimalField(max_digits=18, decimal_places=2)),
            ),
            total_vente_ref=Coalesce(
                Sum(
                    ExpressionWrapper(
                        F("quantite") * F("prix_vente_unitaire"),
                        output_field=DecimalField(max_digits=18, decimal_places=2),
                    )
                ),
                Value(0, output_field=DecimalField(max_digits=18, decimal_places=2)),
            ),
        )
        .order_by("-total_achat")
    )

    items = []
    for r in rows:
        qte = int(r["qte_total"] or 0)
        total_achat = float(r["total_achat"] or 0)
        total_vente_ref = float(r["total_vente_ref"] or 0)

        prix_moyen_achat = int(total_achat / qte) if qte else 0
        prix_moyen_vente = int(total_vente_ref / qte) if qte else 0

        items.append({
            "article_id": int(r["article_id"]),
            "reference": r["article__reference"] or "",
            "nom_produit": r["article__nom_produit"] or "",
            "quantite": qte,  # ✅ output attendu
            "prix_moyen_achat": int(prix_moyen_achat),
            "prix_moyen_vente": int(prix_moyen_vente),
            "total_achat": int(total_achat),
        })

    limit = (request.query_params.get("limit") or "").strip()
    if limit.isdigit():
        items = items[: int(limit)]

    return Response({
        "range": {"date_from": dfrom.isoformat(), "date_to": dto.isoformat()},
        "items": items,
    })
