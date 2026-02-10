# user/serializers.py
from __future__ import annotations

from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    email = serializers.EmailField(required=True)
    username = serializers.CharField(required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ["first_name", "last_name", "username", "email", "password"]

    def validate_username(self, value):
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("Ce nom d’utilisateur est déjà utilisé.")
        return value

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Cet email est déjà utilisé.")
        return value

    def create(self, validated_data):
        password = validated_data.pop("password")
        # ✅ role par défaut = COMMERCIALE via manager
        user = User.objects.create_user(password=password, **validated_data)
        return user


class MeSerializer(serializers.ModelSerializer):
    photo_profil_url = serializers.SerializerMethodField()
    photo_couverture_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id", "username", "email", "first_name", "last_name", "role",
            "adresse", "numero_telephone", "sexe",
            "photo_profil_url", "photo_couverture_url",
        ]

    def _abs(self, request, url: str) -> str:
        return request.build_absolute_uri(url) if request else url

    def get_photo_profil_url(self, obj):
        request = self.context.get("request")
        if not obj.photo_profil:
            return None
        return self._abs(request, obj.photo_profil.url)

    def get_photo_couverture_url(self, obj):
        request = self.context.get("request")
        if not obj.photo_couverture:
            return None
        return self._abs(request, obj.photo_couverture.url)


class UpdateProfileSerializer(serializers.ModelSerializer):
    """
    ✅ L’utilisateur peut modifier SON profil (pas le role).
    """
    class Meta:
        model = User
        fields = [
            "first_name", "last_name",
            "adresse", "numero_telephone", "sexe",
            "photo_profil", "photo_couverture",
        ]


class AdminSetRoleSerializer(serializers.Serializer):
    role = serializers.ChoiceField(choices=User.Role.choices)

    def validate_role(self, value):
        # sécurité: role ADMIN ne doit pas être donné à n'importe qui (optionnel)
        # si tu veux autoriser l’admin à promouvoir quelqu’un admin, laisse.
        return value
