# achats/views.py
from rest_framework import viewsets, permissions
from django.db.models import Prefetch

from .models import Achat, AchatLigne
from .serializers import AchatSerializer


class AchatViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AchatSerializer

    def get_queryset(self):
        qs = (
            Achat.objects
            .prefetch_related(
                Prefetch("lignes", queryset=AchatLigne.objects.select_related("article"))
            )
            .order_by("-id")
        )
        return qs

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["request"] = self.request
        return ctx
