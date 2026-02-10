# dashboard/views.py
from __future__ import annotations

from datetime import date

from django.db.models import (
    Count, Sum, F, Q, Value, IntegerField, DecimalField, ExpressionWrapper
)
from django.db.models.functions import Coalesce, TruncDay, Cast
from django.utils.dateparse import parse_date

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from vente.models import Commande, LigneCommande
from encaissement.models import Encaissement


def _parse_dates(request):
    dfrom = parse_date((request.query_params.get("date_from") or "").strip())
    dto = parse_date((request.query_params.get("date_to") or "").strip())

    # fallback: mois courant si rien
    today = date.today()
    if not dfrom:
        dfrom = today.replace(day=1)
    if not dto:
        dto = today

    # inclusif -> on filtre created_at__date <= dto
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


def _ca_expr():
    """
    CA articles = SUM(qte * prix_vente_unitaire)
    (calculé au niveau Commande via lignes__)
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

    # Encaisse uniquement (commande avec encaissement PAYEE)
    qs_paid = qs.filter(encaissement__statut=Encaissement.StatutPaiement.PAYEE)

    agg_paid = qs_paid.aggregate(
        nb=Count("id"),
        ca_articles=ca_articles,
        ca_frais=ca_frais,
    )

    ca_total_encaisse = int(float(agg_paid["ca_articles"] or 0)) + int(agg_paid["ca_frais"] or 0)
    nb_paid = int(agg_paid["nb"] or 0)
    panier_moyen_encaisse = int(ca_total_encaisse / nb_paid) if nb_paid else 0

    return Response({
        "range": {"date_from": dfrom.isoformat(), "date_to": dto.isoformat()},
        "nb_commandes": nb,
        "nb_livrees": int(agg_all["nb_livrees"] or 0),
        "nb_annulees": int(agg_all["nb_annulees"] or 0),
        "ca_total_commandes": ca_total_commandes,
        "ca_total_encaisse": ca_total_encaisse,
        "panier_moyen": panier_moyen,
        "panier_moyen_encaisse": panier_moyen_encaisse,
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

    rows = (
        qs.values("statut")
        .annotate(nb=Count("id"))
        .order_by("statut")
    )

    return Response({
        "range": {"date_from": dfrom.isoformat(), "date_to": dto.isoformat()},
        "items": [{"statut": r["statut"], "nb": int(r["nb"] or 0)} for r in rows],
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def dashboard_top_articles(request):
    qs, dfrom, dto = _base_qs(request)

    # Option: top sur commandes non annulées
    qs = qs.exclude(statut=Commande.Statut.ANNULEE)

    # ✅ FIX IMPORTANT:
    # Ne pas utiliser alias "quantite" (agrégat) puis F("quantite") dans un autre agrégat.
    # On renomme l'alias en qte_total, et on garde F("quantite") (champ DB) pour calculer CA.
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
            # ✅ on renvoie "quantite" comme ton frontend attend
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

    # uniquement encaisse PAYEE
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
        items.append({
            "mode": r["encaissement__mode"] or "",
            "nb": int(r["nb"] or 0),
            "ca": ca,
        })

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
