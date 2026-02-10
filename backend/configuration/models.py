# configuration/models.py
from __future__ import annotations

from django.db import models
from django.core.validators import RegexValidator


class AppConfiguration(models.Model):
    """
    Configuration globale (singleton) pour contrôler l'app.
    Tu peux ajouter des champs plus tard (maintenance_mode, support_phone, etc.)
    """
    app_name = models.CharField(max_length=120, default="Mon Application")
    maintenance_mode = models.BooleanField(default=False)
    maintenance_message = models.CharField(max_length=255, blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Configuration globale"
        verbose_name_plural = "Configuration globale"

    def __str__(self) -> str:
        return f"AppConfiguration({self.app_name})"

    @classmethod
    def get_solo(cls) -> "AppConfiguration":
        obj = cls.objects.order_by("id").first()
        if obj:
            return obj
        return cls.objects.create(app_name="Mon Application")


class Page(models.Model):
    """
    Page configurable (menu, dashboard, raccourcis, etc.)
    """
    config = models.ForeignKey(
        AppConfiguration,
        on_delete=models.CASCADE,
        related_name="pages",
    )

    nom = models.CharField(max_length=120)

    # lien peut être:
    # - /encaissement
    # - /vente/commandes
    # - https://google.com
    lien = models.CharField(max_length=255)

    logo = models.ImageField(upload_to="configuration/pages/", blank=True, null=True)

    ordre = models.PositiveIntegerField(default=0)
    actif = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["ordre", "id"]
        unique_together = [("config", "nom")]

    def __str__(self) -> str:
        return f"{self.nom} ({self.lien})"
