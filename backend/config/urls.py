# project/urls.py (racine)
from django.contrib import admin
from django.urls import path, include
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.conf import settings
from django.conf.urls.static import static

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

@api_view(["GET"])
@permission_classes([AllowAny])
def health(request):
    return Response({"status": "ok"})

urlpatterns = [
    path("admin/", admin.site.urls),

    # ✅ Health direct (sans include)
    path("api/health/", health, name="api_health"),

    # ✅ Auth JWT
    path("api/auth/login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    # # ✅ Users app (tes endpoints: me, logout, register, etc.)
    path("api/auth/", include("user.urls")),

    # ✅ Clients app (CRUD clients)
    path("api/", include("client.urls")),

    # pour les articles
    path("api/", include("article.urls")),

    # livraison
    path("api/livraison/", include("livraison.urls")),

    # achats
    path("api/achats/", include("achats.urls")),

    # ventes
    path("api/vente/", include("vente.urls")),

    # encaissement
    path("api/encaissement/", include("encaissement.urls")),

    # configuration
    path("api/configuration/", include("configuration.urls")),

    # facturation
    path("api/facturation/", include("facturation.urls")),

    # dashboard
    path("api/dashboard/", include("dashboard.urls")),

    # livraison
    # ✅ AJOUT ICI
    path("api/conflivraison/", include("conflivraison.urls")),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
