from rest_framework import serializers
from .models import LieuLivraison, FraisLivraison, default_frais_par_categorie


class LieuLivraisonSerializer(serializers.ModelSerializer):
    default_frais = serializers.SerializerMethodField()

    class Meta:
        model = LieuLivraison
        fields = ["id", "nom", "categorie", "actif", "default_frais", "created_at", "updated_at"]
        read_only_fields = ["default_frais", "created_at", "updated_at"]

    def get_default_frais(self, obj: LieuLivraison) -> int:
        return int(default_frais_par_categorie(obj.categorie))


class FraisLivraisonSerializer(serializers.ModelSerializer):
    lieu_detail = LieuLivraisonSerializer(source="lieu", read_only=True)

    class Meta:
        model = FraisLivraison
        fields = [
            "id",
            "lieu",
            "lieu_detail",
            "frais_calcule",
            "frais_override",
            "frais_final",
            "note",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["frais_calcule", "frais_final", "created_at", "updated_at"]

    def validate_frais_override(self, value):
        if value in (None, "", "null"):
            return None
        return int(value)
