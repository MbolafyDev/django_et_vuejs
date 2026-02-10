# encaissement/models.py
from __future__ import annotations

from django.db import models
from django.conf import settings
from django.utils import timezone

from vente.models import Commande


class Encaissement(models.Model):
    class StatutPaiement(models.TextChoices):
        EN_ATTENTE = "EN_ATTENTE", "En attente"
        PAYEE = "PAYEE", "Payée"
        ANNULEE = "ANNULEE", "Annulée"

    class ModePaiement(models.TextChoices):
        ESPECE = "ESPECE", "Espèce"
        MVOLA = "MVOLA", "MVola"
        ORANGE_MONEY = "ORANGE_MONEY", "Orange Money"

    commande = models.OneToOneField(
        Commande,
        on_delete=models.CASCADE,
        related_name="encaissement",
    )

    statut = models.CharField(
        max_length=20,
        choices=StatutPaiement.choices,
        default=StatutPaiement.EN_ATTENTE,
    )

    mode = models.CharField(
        max_length=20,
        choices=ModePaiement.choices,
        blank=True,
        default="",
    )

    reference = models.CharField(max_length=120, blank=True, default="")

    encaisse_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="encaissements",
    )

    encaisse_le = models.DateTimeField(null=True, blank=True)

    note = models.TextField(blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-id"]

    def mark_paid(self, *, user=None, mode: str, reference: str = ""):
        self.statut = self.StatutPaiement.PAYEE
        self.mode = mode
        self.reference = reference or ""
        self.encaisse_par = user if user and getattr(user, "is_authenticated", False) else None
        self.encaisse_le = timezone.now()

    def mark_cancelled(self, *, user=None, note: str = ""):
        self.statut = self.StatutPaiement.ANNULEE
        self.encaisse_par = user if user and getattr(user, "is_authenticated", False) else None
        if note:
            self.note = note

    def __str__(self) -> str:
        return f"Encaissement #{self.id} - Commande #{self.commande_id} - {self.statut}"
