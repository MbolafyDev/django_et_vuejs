# accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        "id", "username", "email", "first_name", "last_name",
        "role", "is_staff", "is_superuser", "is_active", "date_joined",
    )
    list_filter = ("role", "is_staff", "is_superuser", "is_active", "groups")
    search_fields = ("username", "email", "first_name", "last_name", "numero_telephone")
    ordering = ("-date_joined",)

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Informations personnelles"), {
            "fields": (
                "first_name", "last_name", "email",
                "role",
                "photo_profil", "photo_couverture",
                "adresse", "numero_telephone", "sexe",
            )
        }),
        (_("Permissions"), {
            "fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")
        }),
        (_("Dates importantes"), {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "username", "email",
                "first_name", "last_name",
                "password1", "password2",
                "is_staff", "is_superuser",
                "role",
            ),
        }),
    )

    filter_horizontal = ("groups", "user_permissions")
