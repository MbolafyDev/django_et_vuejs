# vente/admin.py
from django.contrib import admin
from .models import Commande

@admin.register(Commande)
class CommandeAdmin(admin.ModelAdmin):
    search_fields = ("id",)  # minimum requis pour autocomplete
