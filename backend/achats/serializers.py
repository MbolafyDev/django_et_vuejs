# achats/serializers.py
from __future__ import annotations
from django.db import transaction
from rest_framework import serializers
from article.models import Article
from .models import Achat, AchatLigne


class ArticleMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ["id", "nom_produit", "reference", "prix_achat", "prix_vente", "quantite_stock"]


class AchatLigneSerializer(serializers.ModelSerializer):
    article_detail = ArticleMiniSerializer(source="article", read_only=True)

    class Meta:
        model = AchatLigne
        fields = [
            "id",
            "article",
            "article_detail",
            "quantite",
            "prix_achat_unitaire",
            "prix_vente_unitaire",
            "maj_prix_article",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]


class AchatSerializer(serializers.ModelSerializer):
    lignes = AchatLigneSerializer(many=True)

    total = serializers.SerializerMethodField()

    class Meta:
        model = Achat
        fields = [
            "id",
            "fournisseur",
            "date_achat",
            "note",
            "lignes",
            "total",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["total", "created_at", "updated_at"]

    def get_total(self, obj: Achat):
        return obj.total

    @transaction.atomic
    def create(self, validated_data):
        lignes_data = validated_data.pop("lignes", [])
        request = self.context.get("request")

        achat = Achat.objects.create(
            user=getattr(request, "user", None),
            **validated_data
        )

        for ld in lignes_data:
            ligne = AchatLigne.objects.create(achat=achat, **ld)
            self._apply_stock_and_prices_on_create(ligne)

        return achat

    @transaction.atomic
    def update(self, instance: Achat, validated_data):
        lignes_data = validated_data.pop("lignes", None)

        # update champs achat
        for k, v in validated_data.items():
            setattr(instance, k, v)
        instance.save()

        if lignes_data is None:
            return instance

        # Stratégie simple et sûre :
        # 1) rollback stock de toutes les anciennes lignes
        # 2) supprimer anciennes lignes
        # 3) recréer nouvelles lignes + appliquer stock/prix
        old_lines = list(instance.lignes.select_related("article").all())
        for old in old_lines:
            self._rollback_stock_on_delete(old)

        instance.lignes.all().delete()

        for ld in lignes_data:
            new_line = AchatLigne.objects.create(achat=instance, **ld)
            self._apply_stock_and_prices_on_create(new_line)

        return instance

    # -------------------------
    # Helpers stock/prix
    # -------------------------
    def _apply_stock_and_prices_on_create(self, ligne: AchatLigne):
        art = ligne.article
        # ✅ stock +quantité
        art.quantite_stock = int(art.quantite_stock) + int(ligne.quantite)

        # ✅ prix article (optionnel)
        if ligne.maj_prix_article:
            if ligne.prix_achat_unitaire is not None:
                art.prix_achat = ligne.prix_achat_unitaire
            if ligne.prix_vente_unitaire is not None:
                art.prix_vente = ligne.prix_vente_unitaire

        art.save(update_fields=["quantite_stock", "prix_achat", "prix_vente", "updated_at"])

    def _rollback_stock_on_delete(self, ligne: AchatLigne):
        art = ligne.article
        art.quantite_stock = int(art.quantite_stock) - int(ligne.quantite)
        if art.quantite_stock < 0:
            art.quantite_stock = 0
        art.save(update_fields=["quantite_stock", "updated_at"])
