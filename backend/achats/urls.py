# achats/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AchatViewSet

router = DefaultRouter()
router.register(r"achats", AchatViewSet, basename="achats")

urlpatterns = [
    path("", include(router.urls)),
]
