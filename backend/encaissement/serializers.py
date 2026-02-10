# encaissement/serializers.py
from __future__ import annotations

from rest_framework import serializers
from django.db import transaction
from django.utils import timezone

from vente.models import Commande, LigneCommande
from vente.serializers import (
    ClientLiteSerializer,
    LieuLivraisonLiteSerializer,
    LigneCommandeReadSerializer,
)
from .models import Encaissement


class CommandeEncaissementListSerializer(serializers.ModelSerializer):
    client_detail = ClientLiteSerializer(source="client", read_only=True)
    lieu_detail = LieuLivraisonLiteSerializer(source="lieu_livraison", read_only=True)
    lignes_detail = LigneCommandeReadSerializer(source="lignes", many=True, read_only=True)

    total_articles = serializers.IntegerField(read_only=True)
    total_commande = serializers.IntegerField(read_only=True)
    frais_final = serializers.SerializerMethodField()

    paiement_statut = serializers.SerializerMethodField()
    paiement_mode = serializers.SerializerMethodField()
    paiement_reference = serializers.SerializerMethodField()
    encaisse_le = serializers.SerializerMethodField()

    class Meta:
        model = Commande
        fields = [
            "id",
            "statut",
            "date_livraison",
            "precision_lieu",
            "note",
            "created_at",
            "updated_at",

            "client_nom",
            "client_contact",
            "client_adresse",

            "client_detail",
            "lieu_detail",
            "lignes_detail",

            "total_articles",
            "frais_final",
            "total_commande",

            "paiement_statut",
            "paiement_mode",
            "paiement_reference",
            "encaisse_le",
        ]

    def get_frais_final(self, obj: Commande) -> int:
        return int(getattr(obj.frais_livraison, "frais_final", 0) or 0)

    def _get_enc(self, obj: Commande) -> Encaissement | None:
        return getattr(obj, "encaissement", None)

    def get_paiement_statut(self, obj: Commande) -> str:
        enc = self._get_enc(obj)
        return enc.statut if enc else Encaissement.StatutPaiement.EN_ATTENTE

    def get_paiement_mode(self, obj: Commande) -> str:
        enc = self._get_enc(obj)
        return enc.mode if enc else ""

    def get_paiement_reference(self, obj: Commande) -> str:
        enc = self._get_enc(obj)
        return enc.reference if enc else ""

    def get_encaisse_le(self, obj: Commande):
        enc = self._get_enc(obj)
        return enc.encaisse_le.isoformat() if enc and enc.encaisse_le else None


class EncaisserCommandeSerializer(serializers.Serializer):
    mode = serializers.ChoiceField(choices=Encaissement.ModePaiement.choices)
    reference = serializers.CharField(required=False, allow_blank=True, default="")
    note = serializers.CharField(required=False, allow_blank=True, default="")

    def validate(self, attrs):
        mode = attrs.get("mode")
        ref = (attrs.get("reference") or "").strip()

        # ✅ Mobile Money => reference obligatoire
        if mode in [Encaissement.ModePaiement.MVOLA, Encaissement.ModePaiement.ORANGE_MONEY]:
            if not ref:
                raise serializers.ValidationError({"reference": "Référence obligatoire pour Mobile Money."})

        return attrs

    @transaction.atomic
    def save(self, *, commande: Commande, user):
        mode = self.validated_data["mode"]
        reference = (self.validated_data.get("reference") or "").strip()
        note = (self.validated_data.get("note") or "").strip()

        enc, _created = Encaissement.objects.select_for_update().get_or_create(commande=commande)

        # ✅ empêche d’encaisser une commande déjà annulée (vente)
        if commande.statut == Commande.Statut.ANNULEE:
            raise serializers.ValidationError("Impossible d'encaisser: la commande est annulée.")

        # ✅ empêche de ré-encaisser si déjà payée
        if enc.statut == Encaissement.StatutPaiement.PAYEE:
            raise serializers.ValidationError("Cette commande est déjà payée.")

        if note:
            enc.note = note

        enc.mark_paid(user=user, mode=mode, reference=reference)
        enc.save()
        return enc


class AnnulerPaiementSerializer(serializers.Serializer):
    note = serializers.CharField(required=False, allow_blank=True, default="")

    @transaction.atomic
    def save(self, *, commande: Commande, user):
        note = (self.validated_data.get("note") or "").strip()
        enc, _created = Encaissement.objects.select_for_update().get_or_create(commande=commande)

        # si déjà payée, tu peux décider:
        # - soit interdit
        # - soit autoriser annulation (remboursement hors scope)
        if enc.statut == Encaissement.StatutPaiement.PAYEE:
            raise serializers.ValidationError("Paiement déjà effectué: annulation non autorisée ici.")

        enc.mark_cancelled(user=user, note=note)
        enc.save()
        return enc
