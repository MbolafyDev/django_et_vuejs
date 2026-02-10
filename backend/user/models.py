from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Utilisateur personnalisé
    - username conservé
    - email unique
    - prêt pour extension future (phone, avatar, etc.)
    """

    email = models.EmailField(
        unique=True,
        blank=False,
        null=False,
        verbose_name="Adresse email",
        error_messages={
            "unique": "Un utilisateur avec cet email existe déjà."
        },
    )

    # 🔮 Extensions futures possibles
    # phone = models.CharField(max_length=20, blank=True)
    # avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)

    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"

    def __str__(self):
        return self.username
