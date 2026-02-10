# facturation/admin.py
from django.contrib import admin
from facturation.models import Facture, FacturationSettings


@admin.register(Facture)
class FactureAdmin(admin.ModelAdmin):
    list_display = ("id", "numero", "date_emission", "commande")
    search_fields = ("numero", "commande__id", "commande__client_nom")
    list_select_related = ("commande",)


@admin.register(FacturationSettings)
class FacturationSettingsAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return not FacturationSettings.objects.exists()
