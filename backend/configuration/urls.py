# configuration/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import AppConfigurationViewSet, PageViewSet

router = DefaultRouter()
router.register(r"pages", PageViewSet, basename="configuration-pages")

urlpatterns = [
    # ✅ maintenant le frontend /configuration/app/solo/ marche
    path("app/solo/", AppConfigurationViewSet.as_view({"get": "solo", "patch": "solo"}), name="configuration-solo"),
    path("", include(router.urls)),
]
