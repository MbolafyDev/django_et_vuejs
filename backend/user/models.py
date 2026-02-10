# user/models.py
from __future__ import annotations

from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import RegexValidator


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, username: str, email: str, password: str | None, **extra_fields):
        if not email:
            raise ValueError("L'adresse email est obligatoire.")
        if not username:
            raise ValueError("Le username est obligatoire.")

        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username: str, email: str, password: str | None = None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        # ✅ Par défaut, un compte est COMMERCIALE
        extra_fields.setdefault("role", User.Role.COMMERCIALE)
        return self._create_user(username, email, password, **extra_fields)

    def create_superuser(self, username: str, email: str, password: str | None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        # ✅ Admin via createsuperuser
        extra_fields.setdefault("role", User.Role.ADMIN)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(username, email, password, **extra_fields)


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        COMMERCIALE = "COMMERCIALE", "Commerciale"
        COMMUNITY_MANAGER = "COMMUNITY_MANAGER", "Community manager"

    class Sexe(models.TextChoices):
        M = "M", "Masculin"
        F = "F", "Féminin"
        AUTRE = "AUTRE", "Autre"

    email = models.EmailField(
        unique=True,
        blank=False,
        null=False,
        verbose_name="Adresse email",
        error_messages={"unique": "Un utilisateur avec cet email existe déjà."},
    )

    role = models.CharField(
        max_length=32,
        choices=Role.choices,
        default=Role.COMMERCIALE,
    )

    # ✅ Champs profil demandés
    photo_profil = models.ImageField(upload_to="users/profil/", blank=True, null=True)
    photo_couverture = models.ImageField(upload_to="users/couverture/", blank=True, null=True)
    adresse = models.CharField(max_length=255, blank=True, default="")

    phone_regex = RegexValidator(
        regex=r"^\+?[0-9 \-]{6,20}$",
        message="Numéro invalide. Exemple: +261 34 00 000 00"
    )
    numero_telephone = models.CharField(max_length=30, blank=True, validators=[phone_regex], default="")

    sexe = models.CharField(max_length=10, choices=Sexe.choices, blank=True, default="")

    objects = UserManager()

    def save(self, *args, **kwargs):
        # ✅ sécurité: si superuser => role ADMIN
        if self.is_superuser:
            self.role = self.Role.ADMIN
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.username} ({self.email})"
