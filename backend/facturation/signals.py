# facturation/signals.py
from __future__ import annotations

from django.db.models.signals import post_save
from django.dispatch import receiver

from vente.models import Commande
from encaissement.models import Encaissement
from facturation.models import Facture


@receiver(post_save, sender=Commande)
def create_facture_for_commande(sender, instance: Commande, created: bool, **kwargs):
    """
    Dès qu'une commande existe, on crée une Facture (proforma par défaut).
    """
    if not instance.pk:
        return

    Facture.objects.get_or_create(
        commande=instance,
        defaults={"numero": Facture.build_next_num()},
    )


@receiver(post_save, sender=Encaissement)
def ensure_facture_exists_when_paid(sender, instance: Encaissement, created: bool, **kwargs):
    """
    Si encaissement PAYEE => la facture devient Facture (type calculé),
    on s'assure qu'une Facture existe.
    """
    cmd = instance.commande
    cmd_id = getattr(cmd, "id", None)
    if not cmd_id:
        return

    Facture.objects.get_or_create(
        commande=cmd,
        defaults={"numero": Facture.build_next_num()},
    )
