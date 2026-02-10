# articles/serializers.py
from rest_framework import serializers
from .models import Article

class ArticleSerializer(serializers.ModelSerializer):
    nom_produit = serializers.CharField(required=True, allow_blank=False)
    reference = serializers.CharField(required=True, allow_blank=False)

    # ✅ renvoyer URL complète si possible
    photo_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Article
        fields = [
            "id",
            "nom_produit",
            "reference",
            "prix_achat",
            "prix_vente",
            "description",
            "photo",       # ✅ pour upload
            "photo_url",   # ✅ pour affichage
            "created_at",
            "updated_at",
        ]

    def get_photo_url(self, obj: Article):
        request = self.context.get("request")
        if obj.photo and hasattr(obj.photo, "url"):
            if request:
                return request.build_absolute_uri(obj.photo.url)
            return obj.photo.url
        return None
