# vente/models.py
from __future__ import annotations

from django.db import models
from django.conf import settings

from client.models import Client
from article.models import Article
from livraison.models import LieuLivraison, FraisLivraison
from configuration.models import Page


class Commande(models.Model):
    class Statut(models.TextChoices):
        EN_ATTENTE = "EN_ATTENTE", "En attente"      # ✅ NEW (forcé)
        EN_LIVRAISON = "EN_LIVRAISON", "En livraison"
        LIVREE = "LIVREE", "Livrée"
        ANNULEE = "ANNULEE", "Annulée"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="commandes",
    )

    page = models.ForeignKey(
        Page,
        on_delete=models.PROTECT,
        related_name="commandes",
        null=True,
        blank=True,
    )

    client = models.ForeignKey(Client, on_delete=models.PROTECT, related_name="commandes")
    lieu_livraison = models.ForeignKey(LieuLivraison, on_delete=models.PROTECT, related_name="commandes")
    frais_livraison = models.ForeignKey(FraisLivraison, on_delete=models.PROTECT, related_name="commandes")

    precision_lieu = models.CharField(max_length=255, blank=True, default="")

    # ✅ Date de livraison (distincte)
    date_livraison = models.DateField(null=True, blank=True)

    # Snapshot client
    client_nom = models.CharField(max_length=150, blank=True, default="")
    client_contact = models.CharField(max_length=100, blank=True, default="")
    client_adresse = models.CharField(max_length=255, blank=True, default="")

    # ✅ Forcé en attente
    statut = models.CharField(max_length=20, choices=Statut.choices, default=Statut.EN_ATTENTE)

    note = models.TextField(blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)  # ✅ Date commande (source)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-id"]

    @property
    def date_commande(self):
        """✅ Date de commande lisible (date seulement)"""
        return self.created_at.date() if self.created_at else None

    @property
    def total_articles(self) -> int:
        return int(sum((l.sous_total for l in self.lignes.all()), 0))

    @property
    def total_commande(self) -> int:
        return int(self.total_articles) + int(self.frais_livraison.frais_final or 0)

    def sync_client_snapshot(self):
        self.client_nom = self.client.nom or ""
        self.client_contact = self.client.contact or ""
        self.client_adresse = self.client.adresse or ""

    def save(self, *args, **kwargs):
        if self.client_id:
            self.sync_client_snapshot()
        # ✅ sécurité: même si quelqu’un tente de changer le statut
        if not self.statut:
            self.statut = Commande.Statut.EN_ATTENTE
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        d_liv = self.date_livraison.isoformat() if self.date_livraison else "-"
        p = self.page.nom if self.page_id else "-"
        return f"Commande #{self.id} - {self.client_nom} - page:{p} - livraison:{d_liv}"


class LigneCommande(models.Model):
    commande = models.ForeignKey(Commande, on_delete=models.CASCADE, related_name="lignes")
    article = models.ForeignKey(Article, on_delete=models.PROTECT, related_name="lignes_commandes")

    quantite = models.PositiveIntegerField(default=1)
    prix_vente_unitaire = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-id"]

    @property
    def sous_total(self) -> int:
        return int(self.quantite) * int(float(self.prix_vente_unitaire))

    def __str__(self) -> str:
        return f"{self.article.reference} x{self.quantite}"
