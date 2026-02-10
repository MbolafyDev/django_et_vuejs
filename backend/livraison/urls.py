# livraison/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LieuLivraisonViewSet, FraisLivraisonViewSet

router = DefaultRouter()
router.register(r"lieux", LieuLivraisonViewSet, basename="lieux")
router.register(r"frais", FraisLivraisonViewSet, basename="frais")

urlpatterns = [
    path("", include(router.urls)),
]
