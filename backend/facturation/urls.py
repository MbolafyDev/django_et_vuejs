# facturation/urls.py
from rest_framework.routers import DefaultRouter
from facturation.views import CommandeFacturationViewSet

router = DefaultRouter()
router.register(r"commandes", CommandeFacturationViewSet, basename="facturation-commandes")

urlpatterns = router.urls
