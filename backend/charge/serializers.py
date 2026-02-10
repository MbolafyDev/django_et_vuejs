from __future__ import annotations

from rest_framework import serializers
from .models import Charge, ChargeCategorie


class ChargeCategorieSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChargeCategorie
        fields = ["id", "nom", "actif", "ordre"]


class ChargeSerializer(serializers.ModelSerializer):
    categorie_nom = serializers.CharField(source="categorie.nom", read_only=True)
    piece_url = serializers.SerializerMethodField()
    created_by_label = serializers.SerializerMethodField()

    class Meta:
        model = Charge
        fields = [
            "id",
            "created_at", "updated_at",
            "date_charge",
            "categorie", "categorie_nom",
            "libelle", "description",
            "montant",
            "statut", "mode_paiement",
            "commande",
            "created_by", "created_by_label",
            "piece", "piece_url",
        ]
        read_only_fields = ["created_at", "updated_at", "created_by"]

    def get_piece_url(self, obj: Charge):
        request = self.context.get("request")
        if not obj.piece:
            return None
        url = obj.piece.url
        return request.build_absolute_uri(url) if request else url

    def get_created_by_label(self, obj: Charge):
        u = obj.created_by
        if not u:
            return None
        full = f"{getattr(u, 'first_name', '')} {getattr(u, 'last_name', '')}".strip()
        return full or getattr(u, "email", None) or getattr(u, "username", None)


class ChargeCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Charge
        fields = [
            "date_charge",
            "categorie",
            "libelle",
            "description",
            "montant",
            "statut",
            "mode_paiement",
            "commande",
            "piece",
        ]
