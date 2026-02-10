# configuration/serializers.py
from __future__ import annotations

from rest_framework import serializers
from .models import AppConfiguration, Page


class PageSerializer(serializers.ModelSerializer):
    logo_url = serializers.SerializerMethodField()

    class Meta:
        model = Page
        fields = [
            "id",
            "config",        # ✅ read_only
            "nom",
            "lien",
            "logo",
            "logo_url",
            "ordre",         # ✅ read_only
            "actif",         # ✅ read_only
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
