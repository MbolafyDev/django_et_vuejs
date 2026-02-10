# facturation/models.py
from __future__ import annotations

from django.db import models
from django.utils import timezone

from vente.models import Commande


class FacturationSettings(models.Model):
    """
    Singleton: configuration signature/footer facture.
    """
    signature_nom = models.CharField(max_length=120, blank=True, default="")
    signature_titre = models.CharField(max_length=120, blank=True, default="")
    signature_image = models.ImageField(upload_to="facturation/signatures/", null=True, blank=True)
    footer_note = models.CharField(max_length=255, blank=True, default="")

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Facturation - Settings"

    @classmethod
    def get_solo(cls) -> "FacturationSettings":
        obj = cls.objects.first()
        if obj:
            return obj
        return cls.objects.create(
            signature_nom="",
            signature_titre="",
            footer_note="Merci pour votre confiance.",
        )

    def __str__(self) -> str:
        return "FacturationSettings (singleton)"


class Facture(models.Model):
    """
    Une facture est liée à une Commande.
    - Type = PROFORMA si non PAYEE
    - Type = FACTURE si PAYEE
    """
    class Type(models.TextChoices):
        PROFORMA = "PROFORMA", "Proforma"
        FACTURE = "FACTURE", "Facture"

    commande = models.OneToOneField(
        Commande,
        on_delete=models.CASCADE,
        related_name="facture",
    )

    numero = models.CharField(max_length=40, unique=True, db_index=True)
    date_emission = models.DateTimeField(default=timezone.now)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-id"]

    def __str__(self) -> str:
        return f"{self.numero} (Commande #{self.commande_id})"

    # --------- logique type ----------
    @property
    def is_paid(self) -> bool:
        enc = getattr(self.commande, "encaissement", None)
        return bool(enc and enc.statut == "PAYEE")

    @property
    def type_facture(self) -> str:
        return self.Type.FACTURE if self.is_paid else self.Type.PROFORMA

    @property
    def numero_affiche(self) -> str:
        # Option: préfixe PF/F selon statut
        prefix = "F" if self.is_paid else "PF"
        return f"{prefix}-{self.numero}"

    @staticmethod
    def build_next_num() -> str:
        """
        Numéro simple incrémental: YYYYNNNNN
        """
        year = timezone.now().year
        prefix = str(year)
        last = Facture.objects.filter(numero__startswith=prefix).order_by("-numero").first()
        if last and last.numero.startswith(prefix) and len(last.numero) >= 9:
            last_n = int(last.numero[4:])  # après YYYY
        else:
            last_n = 0
        return f"{year}{last_n + 1:05d}"
