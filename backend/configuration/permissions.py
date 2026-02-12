# configuration/permissions.py
from rest_framework.permissions import BasePermission

class CanManageUsers(BasePermission):
    message = "Accès réservé aux administrateurs."

    def has_permission(self, request, view):
        u = request.user
        if not u or not u.is_authenticated:
            return False

        # ✅ superuser/staff toujours OK
        if getattr(u, "is_superuser", False) or getattr(u, "is_staff", False):
            return True

        # ✅ role admin (si tu as un champ role)
        return getattr(u, "role", "") == "ADMIN"
