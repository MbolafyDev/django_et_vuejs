# charge/models.py
from __future__ import annotations

from decimal import Decimal
from django.conf import settings
from django.db import models
from django.utils import timezone


class ChargeCategorie(models.Model):
    nom = models.CharField(max_length=120, unique=True)
    actif = models.BooleanField(default=True)
    ordre = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["ordre", "nom"]

    def __str__(self) -> str:
        return self.nom


class Charge(models.Model):
    STATUT_CHOICES = [
        ("BROUILLON", "Brouillon"),
        ("PAYEE", "Payée"),
        ("ANNULEE", "Annulée"),
    ]

    MODE_PAIEMENT_CHOICES = [
        ("CASH", "Cash"),
        ("MVOLA", "MVola"),
        ("ORANGE_MONEY", "Orange Money"),
        ("VISA", "VISA"),
        ("AUTRE", "Autre"),
    ]

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    date_charge = models.DateField(default=timezone.localdate)
    categorie = models.ForeignKey(ChargeCategorie, on_delete=models.PROTECT, related_name="charges")

    libelle = models.CharField(max_length=200)
    description = models.TextField(blank=True, default="")

    montant = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))

    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default="PAYEE")
    mode_paiement = models.CharField(max_length=20, choices=MODE_PAIEMENT_CHOICES, default="CASH")

    # ✅ optionnel: rattacher une charge à une commande (ex: prime livreur sur une livraison)
    commande = models.ForeignKey(
        "vente.Commande",
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="charges",
    )

    # ✅ qui a créé
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="charges_creees",
    )

    # ✅ preuve (reçu / photo)
    piece = models.FileField(upload_to="charges/pieces/", null=True, blank=True)

    class Meta:
        ordering = ["-date_charge", "-created_at"]
        indexes = [
            models.Index(fields=["date_charge"]),
            models.Index(fields=["statut"]),
            models.Index(fields=["categorie"]),
        ]

    def __str__(self) -> str:
        return f"{self.date_charge} - {self.libelle} ({self.montant})"
