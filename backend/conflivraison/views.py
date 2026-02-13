# conflivraison/views.py
from __future__ import annotations

import json

from django.core.serializers.json import DjangoJSONEncoder
from django.db import transaction
from django.db.models import Q, Exists, OuterRef
from django.utils import timezone

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from conflivraison.models import Livraison, LivraisonEvent
from conflivraison.serializers import (
    LivraisonSerializer,
    LivraisonActionSerializer,
    CommandeProgrammationSerializer,
    ProgrammerCommandeSerializer,
)
from vente.models import Commande


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 200


# =========================
# Helpers statuts Commande
# =========================
def _cmd_statut(name: str):
    return getattr(Commande.Statut, name, None)


def _cmd_final_statuts() -> list[str]:
    ann = _cmd_statut("ANNULEE") or _cmd_statut("ANNULE")
    liv = _cmd_statut("LIVREE")
    return [s for s in [ann, liv] if s]


def _cmd_annule_statut() -> str | None:
    return _cmd_statut("ANNULEE") or _cmd_statut("ANNULE")


def _cmd_confirmee_statut() -> str | None:
    return _cmd_statut("CONFIRMEE")


def _cmd_brouillon_statut() -> str | None:
    return _cmd_statut("BROUILLON")


def _cmd_en_livraison_statut() -> str | None:
    return _cmd_statut("EN_LIVRAISON")


def _cmd_livree_statut() -> str | None:
    return _cmd_statut("LIVREE")


# =========================
# JSON SAFE (FIX)
# =========================
def _json_safe(value):
    """
    Convertit les objets non JSON (date/datetime/Decimal/UUID, etc.)
    en types sérialisables pour JSONField.
    """
    if value is None:
        return None
    return json.loads(json.dumps(value, cls=DjangoJSONEncoder))


# =========================
# Events
# =========================
def _log_event(
    *,
    livraison: Livraison,
    from_s: str,
    to_s: str,
    actor,
    message: str = "",
    meta: dict | None = None,
):
    meta = meta or {}
    meta = _json_safe(meta)  # ✅ FIX: meta devient 100% JSON serializable

    LivraisonEvent.objects.create(
        livraison=livraison,
        from_statut=from_s or "",
        to_statut=to_s or "",
        actor=actor if actor and getattr(actor, "is_authenticated", False) else None,
        message=message or "",
        meta=meta,
    )


def _is_final(statut: str) -> bool:
    return statut in [Livraison.Statut.LIVREE, Livraison.Statut.ANNULEE]


class LivraisonViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = LivraisonSerializer
    pagination_class = StandardResultsSetPagination

    # -------------------------
    # AUTO-SYNC (sans bouton)
    # -------------------------
    def _autosync_missing_livraisons(self):
        """
        Crée automatiquement les livraisons manquantes pour les commandes non finalisées.
        Objectif: la liste s'affiche sans cliquer sur 'Synchroniser'.
        """
        finals = _cmd_final_statuts()

        qs_cmd = Commande.objects.all()
        if finals:
            qs_cmd = qs_cmd.exclude(statut__in=finals)

        # commandes sans livraison
        has_liv = Livraison.objects.filter(commande_id=OuterRef("pk"))
        qs_cmd = qs_cmd.annotate(_has_liv=Exists(has_liv)).filter(_has_liv=False)

        # option: éviter de créer des livraisons si commande n'a aucune date
        qs_cmd = qs_cmd.filter(date_livraison__isnull=False)

        cmds = list(qs_cmd.order_by("-id")[:300])  # cap de sécurité
        if not cmds:
            return 0

        created = 0
        for cmd in cmds:
            liv = Livraison.objects.create(
                commande=cmd,
                statut=Livraison.Statut.A_PREPARER,
                date_prevue=getattr(cmd, "date_livraison", None),
                updated_by=self.request.user,
            )
            _log_event(
                livraison=liv,
                from_s="",
                to_s=liv.statut,
                actor=self.request.user,
                message="Création automatique (autosync) lors du listing",
                meta={"commande_id": cmd.id},
            )
            created += 1

        return created

    # -------------------------
    # Queryset
    # -------------------------
    def get_queryset(self):
        # ✅ autosync avant listing
        if getattr(self, "action", None) == "list":
            self._autosync_missing_livraisons()

        qs = (
            Livraison.objects.select_related(
                "commande",
                "commande__page",
                "commande__client",
                "commande__lieu_livraison",
                "commande__frais_livraison",
                "updated_by",
            )
            .prefetch_related("events")
            .order_by("-id")
        )

        qp = self.request.query_params
        statut = (qp.get("statut") or "").strip()
        q = (qp.get("q") or "").strip()
        date_prevue = (qp.get("date_prevue") or "").strip()

        # ✅ IMPORTANT: "page" réservé à la pagination, donc on utilise page_id
        page_id = (qp.get("page_id") or "").strip()

        if statut:
            qs = qs.filter(statut=statut)

        if date_prevue:
            qs = qs.filter(date_prevue=date_prevue)

        if page_id.isdigit():
            qs = qs.filter(commande__page_id=int(page_id))

        if q:
            qs = qs.filter(
                Q(commande__client_nom__icontains=q)
                | Q(commande__client_contact__icontains=q)
                | Q(commande__lieu_livraison__nom__icontains=q)
                | Q(commande__id__icontains=q)
            )

        return qs

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["request"] = self.request
        return ctx

    def perform_create(self, serializer):
        obj: Livraison = serializer.save(updated_by=self.request.user)
        _log_event(
            livraison=obj,
            from_s="",
            to_s=obj.statut,
            actor=self.request.user,
            message="Création du suivi livraison",
            meta={"commande_id": obj.commande_id},
        )

    # -------------------------
    # Statut changement
    # -------------------------
    @transaction.atomic
    def _set_statut(self, livraison: Livraison, new_statut: str, payload: dict):
        if _is_final(livraison.statut):
            raise ValueError("Cette livraison est déjà finalisée (livrée/annulée).")

        from_statut = livraison.statut

        valid_statuts = {s for (s, _) in Livraison.Statut.choices}
        if new_statut not in valid_statuts:
            raise ValueError(f"Statut invalide: {new_statut}")

        livraison.statut = new_statut
        livraison.raison = payload.get("raison", livraison.raison) or ""
        livraison.commentaire = payload.get("commentaire", livraison.commentaire) or ""

        if "date_prevue" in payload:
            livraison.date_prevue = payload.get("date_prevue")

        if new_statut == Livraison.Statut.LIVREE and not livraison.date_prevue:
            livraison.date_prevue = timezone.localdate()

        if new_statut == Livraison.Statut.LIVREE:
            livraison.date_reelle = timezone.now()

        if new_statut in [Livraison.Statut.ANNULEE, Livraison.Statut.REPORTEE]:
            livraison.date_reelle = None

        livraison.updated_by = self.request.user
        livraison.save()

        # ---- sync commande ----
        cmd = livraison.commande

        st_en_liv = _cmd_en_livraison_statut()
        st_livree = _cmd_livree_statut()
        st_annule = _cmd_annule_statut()
        st_conf = _cmd_confirmee_statut()

        if new_statut == Livraison.Statut.EN_LIVRAISON:
            if st_en_liv:
                cmd.statut = st_en_liv

        elif new_statut == Livraison.Statut.LIVREE:
            if st_livree:
                cmd.statut = st_livree
            if not getattr(cmd, "date_livraison", None) and livraison.date_prevue:
                cmd.date_livraison = livraison.date_prevue

        elif new_statut == Livraison.Statut.ANNULEE:
            if not st_annule:
                raise ValueError("Statut commande annulation introuvable (ANNULEE/ANNULE).")
            cmd.statut = st_annule

        elif new_statut == Livraison.Statut.REPORTEE:
            if st_en_liv and st_conf and cmd.statut == st_en_liv:
                cmd.statut = st_conf

        update_fields = ["updated_at", "statut", "date_livraison"]
        cmd.save(update_fields=update_fields)

        # ✅ FIX: on peut passer payload avec date_prevue (date) car _log_event rend meta JSON-safe
        _log_event(
            livraison=livraison,
            from_s=from_statut,
            to_s=new_statut,
            actor=self.request.user,
            message=f"Changement statut: {from_statut} -> {new_statut}",
            meta={"payload": payload},
        )

    # -------------------------
    # Actions
    # -------------------------
    @action(detail=True, methods=["post"], url_path="en-livraison")
    def set_en_livraison(self, request, pk=None):
        livraison = self.get_object()
        payload = LivraisonActionSerializer(data=request.data)
        payload.is_valid(raise_exception=True)
        try:
            self._set_statut(livraison, Livraison.Statut.EN_LIVRAISON, payload.validated_data)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        livraison.refresh_from_db()
        return Response(LivraisonSerializer(livraison, context={"request": request}).data)

    @action(detail=True, methods=["post"], url_path="livrer")
    def set_livree(self, request, pk=None):
        livraison = self.get_object()
        payload = LivraisonActionSerializer(data=request.data)
        payload.is_valid(raise_exception=True)
        try:
            self._set_statut(livraison, Livraison.Statut.LIVREE, payload.validated_data)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        livraison.refresh_from_db()
        return Response(LivraisonSerializer(livraison, context={"request": request}).data)

    @action(detail=True, methods=["post"], url_path="annuler")
    def set_annulee(self, request, pk=None):
        livraison = self.get_object()
        payload = LivraisonActionSerializer(data=request.data)
        payload.is_valid(raise_exception=True)
        try:
            self._set_statut(livraison, Livraison.Statut.ANNULEE, payload.validated_data)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        livraison.refresh_from_db()
        return Response(LivraisonSerializer(livraison, context={"request": request}).data)

    @action(detail=True, methods=["post"], url_path="reporter")
    def set_reportee(self, request, pk=None):
        livraison = self.get_object()
        payload = LivraisonActionSerializer(data=request.data)
        payload.is_valid(raise_exception=True)
        try:
            self._set_statut(livraison, Livraison.Statut.REPORTEE, payload.validated_data)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        livraison.refresh_from_db()
        return Response(LivraisonSerializer(livraison, context={"request": request}).data)

    @action(detail=True, methods=["get"], url_path="history")
    def history(self, request, pk=None):
        liv = (
            Livraison.objects.select_related("commande")
            .prefetch_related("events")
            .get(pk=pk)
        )
        return Response(LivraisonSerializer(liv, context={"request": request}).data)

    # -------------------------
    # Commandes à programmer
    # -------------------------
    @action(detail=False, methods=["get"], url_path="commandes-a-programmer")
    def commandes_a_programmer(self, request):
        finals = _cmd_final_statuts()

        qs = (
            Commande.objects.select_related("page", "client", "lieu_livraison", "frais_livraison")
            .order_by("-id")
        )
        if finals:
            qs = qs.exclude(statut__in=finals)

        qp = request.query_params
        q = (qp.get("q") or "").strip()
        page_id = (qp.get("page_id") or "").strip()
        statut = (qp.get("statut") or "").strip()
        date_livraison = (qp.get("date_livraison") or "").strip()

        if statut:
            qs = qs.filter(statut=statut)
        if page_id.isdigit():
            qs = qs.filter(page_id=int(page_id))
        if date_livraison:
            qs = qs.filter(date_livraison=date_livraison)
        if q:
            qs = qs.filter(
                Q(client_nom__icontains=q)
                | Q(client_contact__icontains=q)
                | Q(client_adresse__icontains=q)
                | Q(lieu_livraison__nom__icontains=q)
                | Q(id__icontains=q)
            )

        page = self.paginate_queryset(qs)
        ser = CommandeProgrammationSerializer(page, many=True, context={"request": request})
        return self.get_paginated_response(ser.data)

    # -------------------------
    # Programmer commande
    # -------------------------
    @action(detail=False, methods=["post"], url_path="programmer-commande")
    @transaction.atomic
    def programmer_commande(self, request):
        ser = ProgrammerCommandeSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        commande_id = ser.validated_data["commande_id"]
        date_livraison = ser.validated_data["date_livraison"]

        cmd = Commande.objects.select_for_update().get(id=commande_id)

        finals = _cmd_final_statuts()
        if finals and cmd.statut in finals:
            return Response({"detail": "Commande finalisée (annulée/livrée)."}, status=status.HTTP_400_BAD_REQUEST)

        cmd.date_livraison = date_livraison

        brouillon = _cmd_brouillon_statut()
        conf = _cmd_confirmee_statut()
        if brouillon and conf and cmd.statut == brouillon:
            cmd.statut = conf

        cmd.save(update_fields=["date_livraison", "statut", "updated_at"])

        liv = getattr(cmd, "suivi_livraison", None)
        created = False

        if not liv:
            liv = Livraison.objects.create(
                commande=cmd,
                statut=Livraison.Statut.A_PREPARER,
                date_prevue=date_livraison,
                updated_by=request.user,
            )
            _log_event(
                livraison=liv,
                from_s="",
                to_s=liv.statut,
                actor=request.user,
                message="Création via programmation commande",
                meta={"commande_id": cmd.id},
            )
            created = True
        else:
            if _is_final(liv.statut):
                return Response({"detail": "Livraison déjà finalisée (livrée/annulée)."}, status=status.HTTP_400_BAD_REQUEST)

            liv.date_prevue = date_livraison
            liv.updated_by = request.user
            liv.save(update_fields=["date_prevue", "updated_by", "updated_at"])

            _log_event(
                livraison=liv,
                from_s=liv.statut,
                to_s=liv.statut,
                actor=request.user,
                message="Mise à jour date prévue via programmation commande",
                meta={
                    "commande_id": cmd.id,
                    "date_prevue": date_livraison,  # ✅ ok, json-safe grâce à _log_event
                },
            )

        return Response(
            {
                "commande_id": cmd.id,
                "date_livraison": str(cmd.date_livraison) if cmd.date_livraison else None,
                "livraison_id": liv.id,
                "livraison_created": created,
            }
        )

    # -------------------------
    # Sync manual (garde-le, utile)
    # -------------------------
    @action(detail=False, methods=["post"], url_path="sync-from-commandes")
    def sync_from_commandes(self, request):
        created = self._autosync_missing_livraisons()
        return Response({"created": created})
