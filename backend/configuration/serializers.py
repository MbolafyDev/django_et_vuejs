# configuration/serializers.py
from __future__ import annotations

from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import AppConfiguration, Page

User = get_user_model()


class PageSerializer(serializers.ModelSerializer):
    logo_url = serializers.SerializerMethodField()

    class Meta:
        model = Page
        fields = [
            "id",
            "config",
            "nom",
            "lien",
            "logo",
            "logo_url",
            "ordre",
            "actif",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["config", "ordre", "actif", "created_at", "updated_at"]

    def get_logo_url(self, obj: Page):
        if not obj.logo:
            return None
        request = self.context.get("request")
        url = obj.logo.url
        return request.build_absolute_uri(url) if request else url


class AppConfigurationSerializer(serializers.ModelSerializer):
    pages = PageSerializer(many=True, read_only=True)

    class Meta:
        model = AppConfiguration
        fields = [
            "id",
            "app_name",
            "maintenance_mode",
            "maintenance_message",
            "pages",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]


# =========================================================
# ✅ NEW: Serializer pour la gestion utilisateurs
# =========================================================
class ConfigUserSerializer(serializers.ModelSerializer):
    # si ton user a un champ photo_profil (ImageField)
    photo_profil_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "role",
            "is_active",
            "is_staff",
            "is_superuser",
            "date_joined",
            "last_login",
            "photo_profil_url",
        ]
        read_only_fields = [
            "id",
            "is_staff",
            "is_superuser",
            "date_joined",
            "last_login",
            "photo_profil_url",
        ]

    def get_photo_profil_url(self, obj):
        request = self.context.get("request")

        # 1) si ton modèle expose déjà photo_profil_url
        url = getattr(obj, "photo_profil_url", None)
        if url:
            return url

        # 2) sinon si tu as un ImageField photo_profil
        photo = getattr(obj, "photo_profil", None)
        if photo and hasattr(photo, "url"):
            return request.build_absolute_uri(photo.url) if request else photo.url

        return None
