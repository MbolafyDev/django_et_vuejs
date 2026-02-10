# articles/models.py
from django.db import models

class Article(models.Model):
    nom_produit = models.CharField(max_length=180)
    reference = models.CharField(max_length=80, unique=True)
    prix_achat = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    prix_vente = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    description = models.TextField(blank=True, default="")

    # ✅ stock
    quantite_stock = models.IntegerField(default=0)

    photo = models.ImageField(upload_to="articles/", blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return f"{self.nom_produit} ({self.reference})"
