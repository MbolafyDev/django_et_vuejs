# dashboard/models.py
from __future__ import annotations
from django.db import models


class DashboardSnapshot(models.Model):
    """
    Optionnel: stocker des snapshots (ex: chaque nuit) pour éviter de recalculer.
    Tu peux ignorer ce modèle si tu veux du 100% temps réel.
    """
    date = models.DateField(unique=True)
    payload = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date"]

    def __str__(self) -> str:
        return f"Snapshot {self.date}"
