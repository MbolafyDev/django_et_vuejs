# configuration/views.py
from __future__ import annotations

from django.db.models import Max
from django.contrib.auth import get_user_model

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter

try:
    from django_filters.rest_framework import DjangoFilterBackend
    HAS_DJANGO_FILTER = True
except Exception:
    HAS_DJANGO_FILTER = False

from .models import AppConfiguration, Page
from .serializers import (
    AppConfigurationSerializer,
    PageSerializer,
    ConfigUserSerializer,   # ✅ NEW
)

from .permissions import CanManageUsers

User = get_user_model()

ALLOWED_ROLES = ("ADMIN", "UTILISATEUR", "COMMERCIALE", "COMMUNITY_MANAGER")


class AppConfigurationViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def _get_obj(self) -> AppConfiguration:
        return AppConfiguration.get_solo()

    @action(detail=False, methods=["get", "patch"], url_path="solo")
    def solo(self, request):
        obj = self._get_obj()

        if request.method.lower() == "patch":
            ser = AppConfigurationSerializer(obj, data=request.data, partial=True, context={"request": request})
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

        if actif in ["true", "1", "yes", "y", "on"]:
            qs = qs.filter(actif=True)
        elif actif in ["false", "0", "no", "n", "off"]:
            qs = qs.filter(actif=False)

        return qs

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["request"] = self.request
        return ctx

    def perform_create(self, serializer):
        cfg = AppConfiguration.get_solo()
        max_ordre = Page.objects.filter(config=cfg).aggregate(m=Max("ordre")).get("m") or 0
        next_ordre = int(max_ordre) + 1
        serializer.save(config=cfg, ordre=next_ordre, actif=True)

    def perform_update(self, serializer):
        serializer.save()

    @action(detail=True, methods=["patch"], url_path="set-actif")
    def set_actif(self, request, pk=None):
        obj: Page = self.get_object()
        actif = request.data.get("actif", None)

        if actif is None:
            return Response({"detail": "actif requis."}, status=status.HTTP_400_BAD_REQUEST)

        if isinstance(actif, str):
            actif = actif.strip().lower() in ("1", "true", "yes", "y", "on")

        obj.actif = bool(actif)
        obj.save(update_fields=["actif"])
        return Response({"ok": True, "id": obj.id, "actif": obj.actif}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["patch"], url_path="set-ordre")
    def set_ordre(self, request, pk=None):
        obj: Page = self.get_object()
        ordre = request.data.get("ordre", None)

        if ordre is None:
            return Response({"detail": "ordre requis."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            ordre_int = int(ordre)
        except Exception:
            return Response({"detail": "ordre doit être un entier."}, status=status.HTTP_400_BAD_REQUEST)

        obj.ordre = ordre_int
        obj.save(update_fields=["ordre"])
        return Response({"ok": True, "id": obj.id, "ordre": obj.ordre}, status=status.HTTP_200_OK)


class ConfigUserViewSet(viewsets.ModelViewSet):
    """
    ✅ Gestion utilisateurs (ADMIN / staff / superuser)
    - GET /configuration/users/
    - GET /configuration/users/{id}/
    - PATCH /configuration/users/{id}/set-status/
    - PATCH /configuration/users/{id}/set-role/
    """
    queryset = User.objects.all().order_by("-id")
    serializer_class = ConfigUserSerializer  # ✅ FIX CRITIQUE (sinon 500)
    permission_classes = [permissions.IsAuthenticated]

    # search / ordering / filters
    filter_backends = [SearchFilter, OrderingFilter] + ([DjangoFilterBackend] if HAS_DJANGO_FILTER else [])
    search_fields = ["username", "email", "first_name", "last_name"]
    ordering_fields = ["id", "username", "email", "role", "is_active", "date_joined", "last_login"]

    if HAS_DJANGO_FILTER:
        filterset_fields = ["role", "is_active"]

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["request"] = self.request
        return ctx

    def get_permissions(self):
        # ✅ On protège tout le module users par CanManageUsers (plus logique)
        # (tu peux laisser list public auth si tu veux, mais ici: admin-only)
        if self.action in (
            "list",
            "retrieve",
            "set_role",
            "set_status",
            "create",
            "update",
            "partial_update",
            "destroy",
        ):
            return [permissions.IsAuthenticated(), CanManageUsers()]
        return [permissions.IsAuthenticated()]

    @action(detail=True, methods=["patch"], url_path="set-status")
    def set_status(self, request, pk=None):
        u = self.get_object()
        is_active = request.data.get("is_active", None)

        if is_active is None:
            return Response({"detail": "is_active requis."}, status=status.HTTP_400_BAD_REQUEST)

        if isinstance(is_active, str):
            is_active = is_active.strip().lower() in ("1", "true", "yes", "y", "on")

        u.is_active = bool(is_active)
        u.save(update_fields=["is_active"])

        return Response(self.get_serializer(u).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["patch"], url_path="set-role")
    def set_role(self, request, pk=None):
        u = self.get_object()
        role = (request.data.get("role") or "").strip()

        if role not in ALLOWED_ROLES:
            return Response(
                {"detail": f"Rôle invalide. Choix: {list(ALLOWED_ROLES)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ✅ anti-lock: empêcher que quelqu'un te retire ton admin par accident
        if request.user.id == u.id and role != getattr(u, "role", None):
            return Response({"detail": "Impossible de modifier votre propre rôle."}, status=status.HTTP_400_BAD_REQUEST)

        u.role = role
        u.save(update_fields=["role"])

        return Response(self.get_serializer(u).data, status=status.HTTP_200_OK)
