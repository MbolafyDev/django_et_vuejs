# livraison/views.py
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import LieuLivraison, FraisLivraison, default_frais_par_categorie
from .serializers import LieuLivraisonSerializer, FraisLivraisonSerializer


class LieuLivraisonViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = LieuLivraison.objects.all().order_by("nom")
    serializer_class = LieuLivraisonSerializer

    def get_queryset(self):
        qs = super().get_queryset()

        # ?actif=1
        actif = self.request.query_params.get("actif")
        if actif in ("1", "true", "True"):
            qs = qs.filter(actif=True)

        # ?q=ananarivo
        q = (self.request.query_params.get("q") or "").strip()
        if q:
            qs = qs.filter(nom__icontains=q)

        # ?categorie=VILLE
        categorie = (self.request.query_params.get("categorie") or "").strip()
        if categorie:
            qs = qs.filter(categorie=categorie)

        return qs

    @action(detail=True, methods=["get"])
    def frais_defaut(self, request, pk=None):
        lieu = self.get_object()
        fee = default_frais_par_categorie(lieu.categorie)
        return Response({"lieu_id": lieu.id, "categorie": lieu.categorie, "frais_defaut": fee})


class FraisLivraisonViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = FraisLivraison.objects.select_related("lieu").all().order_by("-created_at")
    serializer_class = FraisLivraisonSerializer

    def get_queryset(self):
        qs = super().get_queryset()

        # ?lieu=3
        lieu = self.request.query_params.get("lieu")
        if lieu:
            qs = qs.filter(lieu_id=lieu)

        # ?categorie=VILLE (via lieu)
        categorie = (self.request.query_params.get("categorie") or "").strip()
        if categorie:
            qs = qs.filter(lieu__categorie=categorie)

        return qs

    @action(detail=False, methods=["post"])
    def calculer(self, request):
        """
        Prévisualiser sans sauvegarder
        Body:
          { "lieu": 1, "frais_override": 4500 (optionnel) }
        """
        lieu_id = request.data.get("lieu")
        if not lieu_id:
            return Response({"detail": "Champ 'lieu' requis."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            lieu = LieuLivraison.objects.get(pk=lieu_id)
        except LieuLivraison.DoesNotExist:
            return Response({"detail": "Lieu introuvable."}, status=status.HTTP_404_NOT_FOUND)

        frais_calc = default_frais_par_categorie(lieu.categorie)
        raw_override = request.data.get("frais_override", None)

        if raw_override in (None, "", "null"):
            override = None
            frais_final = frais_calc
        else:
            override = int(raw_override)
            frais_final = override

        return Response(
            {
                "lieu_id": lieu.id,
                "categorie": lieu.categorie,
                "frais_calculé": frais_calc,
                "frais_override": override,
                "frais_final": frais_final,
            }
        )
