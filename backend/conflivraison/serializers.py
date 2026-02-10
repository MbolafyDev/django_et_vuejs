# conflivraison/serializers.py
from __future__ import annotations

from rest_framework import serializers
from conflivraison.models import Livraison, LivraisonEvent
from vente.models import Commande


class LivraisonEventSerializer(serializers.ModelSerializer):
    actor_name = serializers.SerializerMethodField()

    class Meta:
        model = LivraisonEvent
        fields = ["id", "from_statut", "to_statut", "message", "meta", "actor", "actor_name", "created_at"]

    def get_actor_name(self, obj: LivraisonEvent) -> str | None:
        if not obj.actor_id:
            return None
        return getattr(obj.actor, "username", None) or str(obj.actor)


class CommandeMiniSerializer(serializers.ModelSerializer):
    total_commande = serializers.IntegerField(read_only=True)
    total_articles = serializers.IntegerField(read_only=True)

    class Meta:
        model = Commande
        fields = [
            "id",
            "statut",
            "date_livraison",
            "precision_lieu",
            "client_nom",
            "client_contact",
            "client_adresse",
            "total_articles",
            "total_commande",
            "created_at",
            "updated_at",
        ]


class LivraisonSerializer(serializers.ModelSerializer):
    commande_detail = CommandeMiniSerializer(source="commande", read_only=True)
    events = LivraisonEventSerializer(many=True, read_only=True)

    class Meta:
        model = Livraison
        fields = [
            "id",
            "commande",
            "commande_detail",
            "statut",
            "date_prevue",
            "date_reelle",
            "raison",
            "commentaire",
            "updated_by",
            "events",
            "created_at",
            "updated_at",
        ]
        extra_kwargs = {
            "commande": {"write_only": True},
            "updated_by": {"read_only": True},
        }


# ✅ Pour afficher les commandes même si livraison inexistante
class CommandeProgrammationSerializer(serializers.ModelSerializer):
    livraison_id = serializers.SerializerMethodField()
    livraison_statut = serializers.SerializerMethodField()
    date_prevue = serializers.SerializerMethodField()

    class Meta:
        model = Commande
        fields = [
            "id",
            "statut",
            "date_livraison",
            "precision_lieu",
            "client_nom",
            "client_contact",
            "client_adresse",
            "livraison_id",
            "livraison_statut",
            "date_prevue",
            "created_at",
            "updated_at",
        ]

    def get_livraison_id(self, obj: Commande):
        liv = getattr(obj, "suivi_livraison", None)
        return liv.id if liv else None

    def get_livraison_statut(self, obj: Commande):
        liv = getattr(obj, "suivi_livraison", None)
        return liv.statut if liv else None

    def get_date_prevue(self, obj: Commande):
        liv = getattr(obj, "suivi_livraison", None)
        return liv.date_prevue if liv else None


class LivraisonActionSerializer(serializers.Serializer):
    raison = serializers.CharField(required=False, allow_blank=True, default="")
    commentaire = serializers.CharField(required=False, allow_blank=True, default="")
    date_prevue = serializers.DateField(required=False, allow_null=True)


class ProgrammerCommandeSerializer(serializers.Serializer):
    commande_id = serializers.IntegerField()
    date_livraison = serializers.DateField(required=True)
