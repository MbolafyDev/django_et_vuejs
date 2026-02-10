# conflivraison/models.py
from __future__ import annotations

from django.db import models
from django.conf import settings
from django.utils import timezone

from vente.models import Commande


class Livraison(models.Model):
    """
    Suivi de livraison lié à une commande.
    On ne duplique pas toutes les infos : on lit via commande (client/lieu/page...).
    """
    class Statut(models.TextChoices):
        A_PREPARER = "A_PREPARER", "À préparer"
        EN_LIVRAISON = "EN_LIVRAISON", "En livraison"
        LIVREE = "LIVREE", "Livrée"
        ANNULEE = "ANNULEE", "Annulée"
        REPORTEE = "REPORTEE", "Reportée"

    commande = models.OneToOneField(
        Commande,
        on_delete=models.CASCADE,
        related_name="suivi_livraison",
    )

    statut = models.CharField(max_length=20, choices=Statut.choices, default=Statut.A_PREPARER)

    # Dates
    date_prevue = models.DateField(null=True, blank=True)   # par défaut = commande.date_livraison
    date_reelle = models.DateTimeField(null=True, blank=True)

    # Report / Annulation
    raison = models.CharField(max_length=255, blank=True, default="")
    commentaire = models.TextField(blank=True, default="")

    # Actor
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="livraisons_updates",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-id"]

    def __str__(self) -> str:
        return f"Livraison #{self.id} (cmd:{self.commande_id}) - {self.statut}"

    def sync_from_commande(self):
        # si commande a une date_livraison et que date_prevue est vide
        if not self.date_prevue and self.commande_id and self.commande.date_livraison:
            self.date_prevue = self.commande.date_livraison

    def save(self, *args, **kwargs):
        if self.commande_id:
            self.sync_from_commande()
        super().save(*args, **kwargs)


class LivraisonEvent(models.Model):
    """
    Historique des actions (annulée, reportée, livrée...).
    """
    livraison = models.ForeignKey(Livraison, on_delete=models.CASCADE, related_name="events")

    from_statut = models.CharField(max_length=20, blank=True, default="")
    to_statut = models.CharField(max_length=20, blank=True, default="")

    message = models.CharField(max_length=255, blank=True, default="")
    meta = models.JSONField(blank=True, default=dict)

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="livraison_events",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-id"]

    def __str__(self) -> str:
        return f"Event livraison:{self.livraison_id} {self.from_statut}->{self.to_statut}"
