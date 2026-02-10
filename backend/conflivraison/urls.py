# conflivraison/urls.py
from rest_framework.routers import DefaultRouter
from conflivraison.views import LivraisonViewSet

router = DefaultRouter()
router.register(r"livraisons", LivraisonViewSet, basename="livraison")

urlpatterns = router.urls
