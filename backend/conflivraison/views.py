# conflivraison/views.py
from __future__ import annotations

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


def _log_event(*, livraison: Livraison, from_s: str, to_s: str, actor, message: str = "", meta: dict | None = None):
    LivraisonEvent.objects.create(
        livraison=livraison,
        from_statut=from_s or "",
        to_statut=to_s or "",
        actor=actor if actor and getattr(actor, "is_authenticated", False) else None,
        message=message or "",
        meta=meta or {},
    )


def _is_final(statut: str) -> bool:
    return statut in [Livraison.Statut.LIVREE, Livraison.Statut.ANNULEE]


class LivraisonViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = LivraisonSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        qs = (
            Livraison.objects
            .select_related(
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
        page_id = (qp.get("page") or "").strip()

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

    @transaction.atomic
    def _set_statut(self, livraison: Livraison, new_statut: str, payload: dict):
        # ✅ bloquer uniquement si final
        if _is_final(livraison.statut):
            raise ValueError("Cette livraison est déjà finalisée (livrée/annulée).")

        from_statut = livraison.statut

        # ✅ permissif : autoriser toute transition vers un statut valide
        valid_statuts = {s for (s, _) in Livraison.Statut.choices}
        if new_statut not in valid_statuts:
            raise ValueError(f"Statut invalide: {new_statut}")

        livraison.statut = new_statut
        livraison.raison = payload.get("raison", livraison.raison) or ""
        livraison.commentaire = payload.get("commentaire", livraison.commentaire) or ""

        if "date_prevue" in payload:
            livraison.date_prevue = payload.get("date_prevue")

        # si livré sans date_prevue -> date du jour
        if new_statut == Livraison.Statut.LIVREE and not livraison.date_prevue:
            livraison.date_prevue = timezone.localdate()

        # date_reelle si livré
        if new_statut == Livraison.Statut.LIVREE:
            livraison.date_reelle = timezone.now()

        # si annulée/reportée -> pas de date réelle
        if new_statut in [Livraison.Statut.ANNULEE, Livraison.Statut.REPORTEE]:
            livraison.date_reelle = None

        livraison.updated_by = self.request.user
        livraison.save()

        # ✅ sync commande.statut
        cmd = livraison.commande
        if new_statut == Livraison.Statut.EN_LIVRAISON:
            cmd.statut = Commande.Statut.EN_LIVRAISON
        elif new_statut == Livraison.Statut.LIVREE:
            cmd.statut = Commande.Statut.LIVREE
            if not cmd.date_livraison and livraison.date_prevue:
                cmd.date_livraison = livraison.date_prevue
        elif new_statut == Livraison.Statut.ANNULEE:
            cmd.statut = Commande.Statut.ANNULEE
        elif new_statut == Livraison.Statut.REPORTEE:
            # choix: on revient à CONFIRMEE
            if cmd.statut == Commande.Statut.EN_LIVRAISON:
                cmd.statut = Commande.Statut.CONFIRMEE

        cmd.save(update_fields=["statut", "date_livraison", "updated_at"])

        _log_event(
            livraison=livraison,
            from_s=from_statut,
            to_s=new_statut,
            actor=self.request.user,
            message=f"Changement statut: {from_statut} -> {new_statut}",
            meta={"payload": payload},
        )

    # ---------- Actions ----------
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

    # ✅ NEW: endpoint history (corrige bouton Historique)
    @action(detail=True, methods=["get"], url_path="history")
    def history(self, request, pk=None):
        liv = (
            Livraison.objects
            .select_related("commande")
            .prefetch_related("events")
            .get(pk=pk)
        )
        return Response(LivraisonSerializer(liv, context={"request": request}).data)

    # ---------- Commandes à programmer ----------
    @action(detail=False, methods=["get"], url_path="commandes-a-programmer")
    def commandes_a_programmer(self, request):
        qs = (
            Commande.objects
            .select_related("page", "client", "lieu_livraison", "frais_livraison")
            .exclude(statut__in=[Commande.Statut.ANNULEE, Commande.Statut.LIVREE])
            .order_by("-id")
        )

        qp = request.query_params
        q = (qp.get("q") or "").strip()
        page_id = (qp.get("page") or "").strip()
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

    # ---------- Programmer commande ----------
    @action(detail=False, methods=["post"], url_path="programmer-commande")
    @transaction.atomic
    def programmer_commande(self, request):
        ser = ProgrammerCommandeSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        commande_id = ser.validated_data["commande_id"]
        date_livraison = ser.validated_data["date_livraison"]

        cmd = Commande.objects.select_for_update().get(id=commande_id)

        if cmd.statut in [Commande.Statut.ANNULEE, Commande.Statut.LIVREE]:
            return Response({"detail": "Commande finalisée (annulée/livrée)."}, status=status.HTTP_400_BAD_REQUEST)

        cmd.date_livraison = date_livraison
        if cmd.statut == Commande.Statut.BROUILLON:
            cmd.statut = Commande.Statut.CONFIRMEE
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
                meta={"commande_id": cmd.id, "date_prevue": str(date_livraison)},
            )

        return Response({
            "commande_id": cmd.id,
            "date_livraison": str(cmd.date_livraison),
            "livraison_id": liv.id,
            "livraison_created": created,
        })

    # ---------- Sync ----------
    @action(detail=False, methods=["post"], url_path="sync-from-commandes")
    def sync_from_commandes(self, request):
        qs = Commande.objects.exclude(statut__in=[Commande.Statut.ANNULEE, Commande.Statut.LIVREE])

        has_liv = Livraison.objects.filter(commande_id=OuterRef("pk"))
        qs = qs.annotate(_has_liv=Exists(has_liv)).filter(_has_liv=False)

        created = 0
        for cmd in qs:
            liv = Livraison.objects.create(
                commande=cmd,
                statut=Livraison.Statut.A_PREPARER,
                date_prevue=cmd.date_livraison,
                updated_by=request.user,
            )
            _log_event(
                livraison=liv,
                from_s="",
                to_s=liv.statut,
                actor=request.user,
                message="Création via sync",
                meta={"commande_id": cmd.id},
            )
            created += 1

        return Response({"created": created})
