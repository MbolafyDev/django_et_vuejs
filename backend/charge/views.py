# charge/views/py
from __future__ import annotations

from django.db.models import Sum
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Charge, ChargeCategorie
from .serializers import (
    ChargeSerializer,
    ChargeCreateUpdateSerializer,
    ChargeCategorieSerializer,
)


class ChargeCategorieViewSet(viewsets.ModelViewSet):
    queryset = ChargeCategorie.objects.all()
    serializer_class = ChargeCategorieSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        actif = self.request.query_params.get("actif")
        if actif in ("true", "1", "yes"):
            qs = qs.filter(actif=True)
        return qs


class ChargeViewSet(viewsets.ModelViewSet):
    queryset = Charge.objects.select_related("categorie", "created_by").all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return ChargeCreateUpdateSerializer
        return ChargeSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def get_queryset(self):
        qs = super().get_queryset()

        # filtres simples
        date_from = self.request.query_params.get("date_from")
        date_to = self.request.query_params.get("date_to")
        categorie = self.request.query_params.get("categorie")
        statut = self.request.query_params.get("statut")
        q = (self.request.query_params.get("q") or "").strip()

        if date_from:
            qs = qs.filter(date_charge__gte=date_from)
        if date_to:
            qs = qs.filter(date_charge__lte=date_to)
        if categorie:
            qs = qs.filter(categorie_id=categorie)
        if statut:
            qs = qs.filter(statut=statut)
        if q:
            qs = qs.filter(libelle__icontains=q) | qs.filter(description__icontains=q)

        return qs

    @action(detail=False, methods=["GET"])
    def stats(self, request):
        qs = self.get_queryset()
        total = qs.aggregate(s=Sum("montant"))["s"] or 0
        by_statut = qs.values("statut").annotate(total=Sum("montant")).order_by("statut")
        by_cat = qs.values("categorie__nom").annotate(total=Sum("montant")).order_by("-total")[:12]
        return Response({
            "total": float(total),
            "by_statut": list(by_statut),
            "by_categorie": list(by_cat),
        })
