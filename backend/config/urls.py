# project/urls.py (racine)
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@api_view(["GET"])
@permission_classes([AllowAny])
def health(request):
    return Response({"status": "ok"})


urlpatterns = [
    # Admin Django
    path("admin/", admin.site.urls),

    # Health check
    path("api/health/", health, name="api_health"),

    # =========================
    # AUTHENTIFICATION (CUSTOM)
    # =========================
    # login (email), register, logout, me, profile, roles, reset password
    path("api/auth/", include("user.urls")),

    # =========================
    # APPS METIER
    # =========================

    # Clients
    path("api/", include("client.urls")),

    # Articles
    path("api/", include("article.urls")),

    # Livraison
    path("api/livraison/", include("livraison.urls")),

    # Achats
    path("api/achats/", include("achats.urls")),

    # Ventes
    path("api/vente/", include("vente.urls")),

    # Encaissement
    path("api/encaissement/", include("encaissement.urls")),

    # Configuration
    path("api/configuration/", include("configuration.urls")),

    # Facturation
    path("api/facturation/", include("facturation.urls")),

    # Dashboard
    path("api/dashboard/", include("dashboard.urls")),

    # Conflit livraison
    path("api/conflivraison/", include("conflivraison.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
