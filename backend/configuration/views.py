# configuration/views.py
from __future__ import annotations

from django.db.models import Max
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import AppConfiguration, Page
from .serializers import AppConfigurationSerializer, PageSerializer


class AppConfigurationViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def _get_obj(self) -> AppConfiguration:
        return AppConfiguration.get_solo()

    def solo(self, request):
        obj = self._get_obj()

        if request.method.lower() == "patch":
            ser = AppConfigurationSerializer(
                obj,
                data=request.data,
                partial=True,
                context={"request": request},
            )
            ser.is_valid(raise_exception=True)
            ser.save()
            return Response(ser.data, status=status.HTTP_200_OK)

        ser = AppConfigurationSerializer(obj, context={"request": request})
        return Response(ser.data, status=status.HTTP_200_OK)


class PageViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PageSerializer

    def get_queryset(self):
        cfg = AppConfiguration.get_solo()
        qs = Page.objects.filter(config=cfg).order_by("ordre", "id")

        qp = self.request.query_params
        actif = (qp.get("actif") or "").strip().lower()

        if actif in ["true", "1", "yes"]:
            qs = qs.filter(actif=True)
        elif actif in ["false", "0", "no"]:
            qs = qs.filter(actif=False)

        return qs

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["request"] = self.request
        return ctx

    def perform_create(self, serializer):
        cfg = AppConfiguration.get_solo()

        # ✅ ordre auto: max+1
        max_ordre = Page.objects.filter(config=cfg).aggregate(m=Max("ordre")).get("m") or 0
        next_ordre = int(max_ordre) + 1

        # ✅ force actif=True toujours
        serializer.save(config=cfg, ordre=next_ordre, actif=True)

    def perform_update(self, serializer):
        # ✅ empêche modification actif/ordre via API (même si envoyé)
        serializer.save()
