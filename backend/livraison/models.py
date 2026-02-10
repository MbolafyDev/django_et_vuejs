from __future__ import annotations
from django.db import models


class LieuLivraison(models.Model):
    class Categorie(models.TextChoices):
        VILLE = "VILLE", "Ville"
        PERIPHERIE = "PERIPHERIE", "Périphérie"
        PLUS_PERIPHERIE = "PLUS_PERIPHERIE", "Plus périphérie"
        PROVINCE = "PROVINCE", "Province"
        AUTRE = "AUTRE", "Autre (manuel)"

    nom = models.CharField(max_length=120, unique=True)
    categorie = models.CharField(
        max_length=20,
        choices=Categorie.choices,
        default=Categorie.VILLE,
    )
    actif = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.nom} ({self.get_categorie_display()})"


def default_frais_par_categorie(categorie: str) -> int:
    mapping = {
        LieuLivraison.Categorie.VILLE: 3000,
        LieuLivraison.Categorie.PERIPHERIE: 4000,
        LieuLivraison.Categorie.PLUS_PERIPHERIE: 5000,
        LieuLivraison.Categorie.PROVINCE: 3000,
        LieuLivraison.Categorie.AUTRE: 0,
    }
    return int(mapping.get(categorie, 0))


class FraisLivraison(models.Model):
    lieu = models.ForeignKey(LieuLivraison, on_delete=models.PROTECT, related_name="frais")

    # ✅ SANS ACCENT
    frais_calcule = models.PositiveIntegerField(default=0)
    frais_override = models.PositiveIntegerField(null=True, blank=True)
    frais_final = models.PositiveIntegerField(default=0)

    note = models.CharField(max_length=255, blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def compute(self) -> int:
        return default_frais_par_categorie(self.lieu.categorie)

    def save(self, *args, **kwargs):
        self.frais_calcule = self.compute()
        self.frais_final = int(self.frais_override if self.frais_override is not None else self.frais_calcule)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.lieu.nom} -> {self.frais_final} Ar"
