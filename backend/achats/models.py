# achats/models.py
from __future__ import annotations
from django.db import models
from django.conf import settings
from article.models import Article


class Achat(models.Model):
    """
    En-tête d'achat (facture / bon d'achat)
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="achats",
    )

    fournisseur = models.CharField(max_length=180, blank=True, default="")
    date_achat = models.DateField(auto_now_add=False, null=True, blank=True)
    note = models.TextField(blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-id"]

    @property
    def total(self) -> float:
        return sum((l.total_ligne for l in self.lignes.all()), 0)

    def __str__(self) -> str:
        return f"Achat #{self.id}"


class AchatLigne(models.Model):
    """
    Ligne d'achat = un article, quantité, prix achat/vente (optionnellement mis à jour sur l'article)
    """
    achat = models.ForeignKey(Achat, on_delete=models.CASCADE, related_name="lignes")
    article = models.ForeignKey(Article, on_delete=models.PROTECT, related_name="lignes_achats")

    quantite = models.PositiveIntegerField(default=1)

    prix_achat_unitaire = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    prix_vente_unitaire = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    # Si tu ne veux pas écraser les prix article à chaque achat, tu peux désactiver ce flag
    maj_prix_article = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-id"]

    @property
    def total_ligne(self) -> float:
        return float(self.quantite) * float(self.prix_achat_unitaire)

    def __str__(self) -> str:
        return f"{self.article.reference} x{self.quantite}"
