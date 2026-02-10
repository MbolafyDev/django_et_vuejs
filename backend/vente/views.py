# vente/views.py
from __future__ import annotations

from django.db import transaction
from django.db.models import Prefetch, Q
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from vente.models import Commande, LigneCommande
from vente.serializers import (
    CommandeSerializer,
    ArticleLiteSerializer,
    ClientLiteSerializer,
    LieuLivraisonLiteSerializer,
)

from article.models import Article
from client.models import Client
from livraison.models import LieuLivraison


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 200


class CommandeViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CommandeSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        qs = (
            Commande.objects
            .select_related("page", "client", "lieu_livraison", "frais_livraison")
            .prefetch_related(
                Prefetch("lignes", queryset=LigneCommande.objects.select_related("article"))
            )
            .order_by("-id")
        )

        qp = self.request.query_params

        statut = (qp.get("statut") or "").strip()
        client = (qp.get("client") or "").strip()
        lieu = (qp.get("lieu") or "").strip()
        date_livraison = (qp.get("date_livraison") or "").strip()
        date_commande = (qp.get("date_commande") or "").strip()

        # ✅ IMPORTANT: ne JAMAIS utiliser qp.get("page") ici (réservé pagination)
        page_id = (qp.get("page_id") or "").strip()  # ✅ nouveau param pour filtrer "Page"

        if statut:
            qs = qs.filter(statut=statut)

        if client:
            qs = qs.filter(Q(client__nom__icontains=client) | Q(client__contact__icontains=client))

        if lieu:
            qs = qs.filter(lieu_livraison__nom__icontains=lieu)

        if date_livraison:
            qs = qs.filter(date_livraison=date_livraison)

        if date_commande:
            qs = qs.filter(created_at__date=date_commande)

        if page_id.isdigit():
            qs = qs.filter(page_id=int(page_id))

        return qs

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["request"] = self.request
        return ctx

    @action(detail=False, methods=["get"], url_path="suggest/articles")
    def suggest_articles(self, request):
        q = (request.query_params.get("q") or "").strip()
        qs = Article.objects.all().order_by("-id")
        if q:
            qs = qs.filter(Q(nom_produit__icontains=q) | Q(reference__icontains=q))
        return Response(ArticleLiteSerializer(qs[:15], many=True, context={"request": request}).data)

    @action(detail=False, methods=["get"], url_path="suggest/clients")
    def suggest_clients(self, request):
        q = (request.query_params.get("q") or "").strip()
        qs = Client.objects.all().order_by("-id")
        if q:
            qs = qs.filter(Q(nom__icontains=q) | Q(contact__icontains=q))
        return Response(ClientLiteSerializer(qs[:15], many=True).data)

    @action(detail=False, methods=["get"], url_path="suggest/lieux")
    def suggest_lieux(self, request):
        q = (request.query_params.get("q") or "").strip()
        qs = LieuLivraison.objects.filter(actif=True).order_by("nom")
        if q:
            qs = qs.filter(nom__icontains=q)
        return Response(LieuLivraisonLiteSerializer(qs[:15], many=True).data)

    @action(detail=False, methods=["get"], url_path="client-last-lieu")
    def client_last_lieu(self, request):
        client_id = (request.query_params.get("client_id") or "").strip()
        if not client_id.isdigit():
            return Response({"detail": "client_id invalide"}, status=status.HTTP_400_BAD_REQUEST)

        last_cmd = (
            Commande.objects
            .select_related("lieu_livraison", "frais_livraison")
            .filter(client_id=int(client_id))
            .order_by("-id")
            .first()
        )

        if not last_cmd or not last_cmd.lieu_livraison_id:
            return Response(None)

        lieu = last_cmd.lieu_livraison

        return Response({
            "lieu_id": lieu.id,
            "lieu_nom": lieu.nom,
            "frais_auto": int(getattr(last_cmd.frais_livraison, "frais_final", 0) or 0),
            "precision_lieu": last_cmd.precision_lieu or "",
        })

    @transaction.atomic
    def perform_destroy(self, instance: Commande):
        lines = list(instance.lignes.select_related("article").all())
        for l in lines:
            art = l.article
            art.quantite_stock = int(art.quantite_stock) + int(l.quantite)
            art.save(update_fields=["quantite_stock", "updated_at"])
        instance.delete()
