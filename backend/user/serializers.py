from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        min_length=6,
        error_messages={
            "min_length": "Le mot de passe doit contenir au moins 6 caractères."
        }
    )

    email = serializers.EmailField(
        required=True,
        error_messages={
            "required": "L'email est obligatoire.",
            "invalid": "Veuillez entrer une adresse email valide."
        }
    )

    username = serializers.CharField(
        required=True,
        error_messages={
            "required": "Le nom d’utilisateur est obligatoire."
        }
    )

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password",
            "first_name",
            "last_name",
        ]

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

        user = User(
            username=validated_data.get("username"),
            email=validated_data.get("email"),
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
        )

        user.set_password(password)
        user.save()
        return user
