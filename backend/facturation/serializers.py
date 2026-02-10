# facturation/serializers.py
from __future__ import annotations

from rest_framework import serializers

from vente.models import Commande
from encaissement.models import Encaissement
from facturation.models import Facture
from vente.serializers import CommandeSerializer


class CommandeFacturationSerializer(serializers.ModelSerializer):
    commande_detail = CommandeSerializer(source="*", read_only=True)

    # infos facture calculées
    facture_id = serializers.SerializerMethodField()
    type_facture = serializers.SerializerMethodField()
    numero_affiche = serializers.SerializerMethodField()
    is_paid = serializers.SerializerMethodField()

    # logo page
    logo_url = serializers.SerializerMethodField()

    # paiement
    paiement_statut = serializers.SerializerMethodField()
    paiement_mode = serializers.SerializerMethodField()
    paiement_reference = serializers.SerializerMethodField()
    encaisse_le = serializers.SerializerMethodField()

    class Meta:
        model = Commande
        fields = [
            "id",
            "facture_id",
            "type_facture",
            "numero_affiche",
            "is_paid",
            "created_at",

            "logo_url",

            "paiement_statut",
            "paiement_mode",
            "paiement_reference",
            "encaisse_le",

            "commande_detail",
        ]

    def _get_facture(self, obj: Commande) -> Facture | None:
        return getattr(obj, "facture", None)

    def _get_enc(self, obj: Commande) -> Encaissement | None:
        return getattr(obj, "encaissement", None)

    def get_facture_id(self, obj: Commande):
        f = self._get_facture(obj)
        return f.id if f else None

    def get_type_facture(self, obj: Commande) -> str:
        f = self._get_facture(obj)
        if f:
            return f.type_facture
        # fallback si jamais la facture n'existe pas
        enc = self._get_enc(obj)
        return "FACTURE" if (enc and enc.statut == Encaissement.StatutPaiement.PAYEE) else "PROFORMA"

    def get_numero_affiche(self, obj: Commande) -> str:
        f = self._get_facture(obj)
        if f:
            return f.numero_affiche
        return f"PF-{obj.id}"

    def get_is_paid(self, obj: Commande) -> bool:
        f = self._get_facture(obj)
        if f:
            return f.is_paid
        enc = self._get_enc(obj)
        return bool(enc and enc.statut == Encaissement.StatutPaiement.PAYEE)

    def get_logo_url(self, obj: Commande):
        if not getattr(obj, "page_id", None) or not getattr(obj.page, "logo", None):
            return None
        request = self.context.get("request")
        url = obj.page.logo.url
        return request.build_absolute_uri(url) if request else url

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
