# charge/admin.py
from __future__ import annotations

from django.contrib import admin
from django.db.models import Sum
from django.utils.html import format_html
from django.utils import timezone

from .models import Charge, ChargeCategorie


@admin.register(ChargeCategorie)
class ChargeCategorieAdmin(admin.ModelAdmin):
    list_display = ("nom", "actif", "ordre", "nb_charges")
    list_filter = ("actif",)
    search_fields = ("nom",)
    ordering = ("ordre", "nom")
    list_editable = ("actif", "ordre")
    list_per_page = 50

    @admin.display(description="Nb charges")
    def nb_charges(self, obj: ChargeCategorie) -> int:
        return obj.charges.count()


@admin.register(Charge)
class ChargeAdmin(admin.ModelAdmin):
    date_hierarchy = "date_charge"
    list_display = (
        "date_charge",
        "categorie",
        "libelle",
        "montant_fmt",
        "statut",
        "mode_paiement",
        "commande",
        "created_by",
        "piece_link",
        "created_at",
    )
    list_filter = ("statut", "mode_paiement", "categorie", "date_charge")
    search_fields = ("libelle", "description", "categorie__nom", "commande__id")
    autocomplete_fields = ("categorie", "created_by")  # ✅ commande retirée
    ordering = ("-date_charge", "-created_at")
    list_per_page = 50

    fieldsets = (
        ("Charge", {"fields": ("date_charge", "categorie", "libelle", "description")}),
        ("Montant & paiement", {"fields": ("montant", "statut", "mode_paiement")}),
        ("Liens", {"fields": ("commande", "created_by")}),  # commande reste ici
        ("Pièce justificative", {"fields": ("piece",)}),
        ("Système", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )
    readonly_fields = ("created_at", "updated_at")

    actions = ("mark_paid", "mark_cancelled", "mark_draft")

    def save_model(self, request, obj: Charge, form, change):
        if not obj.created_by_id:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    @admin.display(description="Montant")
    def montant_fmt(self, obj: Charge) -> str:
        val = obj.montant or 0
        return f"{val:,.2f}".replace(",", " ").replace(".", ",")

    @admin.display(description="Pièce")
    def piece_link(self, obj: Charge) -> str:
        if not obj.piece:
            return "—"
        return format_html('<a href="{}" target="_blank" rel="noopener">Voir</a>', obj.piece.url)

    @admin.action(description="Marquer comme Payée")
    def mark_paid(self, request, queryset):
        queryset.update(statut="PAYEE", updated_at=timezone.now())

    @admin.action(description="Marquer comme Annulée")
    def mark_cancelled(self, request, queryset):
        queryset.update(statut="ANNULEE", updated_at=timezone.now())

    @admin.action(description="Marquer comme Brouillon")
    def mark_draft(self, request, queryset):
        queryset.update(statut="BROUILLON", updated_at=timezone.now())

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        qs = self.get_queryset(request)
        total = (qs.aggregate(total=Sum("montant")).get("total") or 0)
        extra_context["charge_total"] = f"{total:,.2f}".replace(",", " ").replace(".", ",")
        return super().changelist_view(request, extra_context=extra_context)
