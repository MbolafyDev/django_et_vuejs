# charge/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ChargeViewSet, ChargeCategorieViewSet

router = DefaultRouter()
router.register(r"charges", ChargeViewSet, basename="charge")
router.register(r"categories", ChargeCategorieViewSet, basename="charge-categorie")

urlpatterns = [
    path("", include(router.urls)),
]
