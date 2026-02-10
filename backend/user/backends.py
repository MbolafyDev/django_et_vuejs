# user/backends.py
from __future__ import annotations

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()


class EmailBackend(ModelBackend):
    """
    Permet authenticate(email=..., password=...)
    """
    def authenticate(self, request, username=None, password=None, email=None, **kwargs):
        # DRF/clients peuvent envoyer "username" ou "email"
        login_email = (email or username or "").strip().lower()
        if not login_email or not password:
            return None

        try:
            user = User.objects.get(email__iexact=login_email)
        except User.DoesNotExist:
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
