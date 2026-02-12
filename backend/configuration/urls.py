# configuration/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import AppConfigurationViewSet, PageViewSet, ConfigUserViewSet

router = DefaultRouter()
router.register(r"pages", PageViewSet, basename="configuration-pages")
router.register(r"users", ConfigUserViewSet, basename="configuration-users")  # ✅ NEW

urlpatterns = [
    # ✅ /api/configuration/app/solo/
    path(
        "app/solo/",
        AppConfigurationViewSet.as_view({"get": "solo", "patch": "solo"}),
        name="configuration-solo",
    ),

    # ✅ /api/configuration/pages/...
    # ✅ /api/configuration/users/...
    path("", include(router.urls)),
]
