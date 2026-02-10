# client/models.py
from django.db import models

class Client(models.Model):
    nom = models.CharField(max_length=150)
    adresse = models.CharField(max_length=255, blank=True, default="")
    contact = models.CharField(max_length=100, blank=True, default="")  # tel/email

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return self.nom
