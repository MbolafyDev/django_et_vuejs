# encaissement/views.py
from __future__ import annotations

from django.db.models import Prefetch, Q
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from vente.models import Commande, LigneCommande
from .models import Encaissement
from .serializers import (
    CommandeEncaissementListSerializer,
    EncaisserCommandeSerializer,
    AnnulerPaiementSerializer,
)


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 200


class EncaissementCommandeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Liste + détails des commandes avec infos d'encaissement,
    et actions encaisser/annuler.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CommandeEncaissementListSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        qs = (
            Commande.objects
            .select_related("client", "lieu_livraison", "frais_livraison")
            .prefetch_related(
                Prefetch("lignes", queryset=LigneCommande.objects.select_related("article")),
            )
            .select_related("encaissement")
            .order_by("-id")
        )

        qp = self.request.query_params
        paiement_statut = (qp.get("paiement_statut") or "").strip()  # EN_ATTENTE / PAYEE / ANNULEE
        vente_statut = (qp.get("statut") or "").strip()
        q = (qp.get("q") or "").strip()

        if vente_statut:
            qs = qs.filter(statut=vente_statut)

        if paiement_statut:
            if paiement_statut == Encaissement.StatutPaiement.EN_ATTENTE:
                qs = qs.filter(Q(encaissement__isnull=True) | Q(encaissement__statut=Encaissement.StatutPaiement.EN_ATTENTE))
            else:
                qs = qs.filter(encaissement__statut=paiement_statut)

        if q:
            qs = qs.filter(
                Q(client_nom__icontains=q) |
                Q(client_contact__icontains=q) |
                Q(id__icontains=q)
            )

        return qs

    @action(detail=True, methods=["post"], url_path="encaisser")
    def encaisser(self, request, pk=None):
        commande = self.get_object()
        ser = EncaisserCommandeSerializer(data=request.data, context={"request": request})
        ser.is_valid(raise_exception=True)
        enc = ser.save(commande=commande, user=request.user)
        return Response({"ok": True, "commande_id": commande.id, "paiement_statut": enc.statut}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="annuler-paiement")
    def annuler_paiement(self, request, pk=None):
        commande = self.get_object()
        ser = AnnulerPaiementSerializer(data=request.data, context={"request": request})
        ser.is_valid(raise_exception=True)
        enc = ser.save(commande=commande, user=request.user)
        return Response({"ok": True, "commande_id": commande.id, "paiement_statut": enc.statut}, status=status.HTTP_200_OK)
