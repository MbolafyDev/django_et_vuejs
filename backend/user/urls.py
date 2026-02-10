# user/urls.py
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from . import views

urlpatterns = [
    # Auth custom
    path("register/", views.register, name="auth_register"),
    path("login/", views.login, name="auth_login"),
    path("logout/", views.logout, name="auth_logout"),

    # ✅ IMPORTANT: refresh (pour éviter la déconnexion)
    path("refresh/", TokenRefreshView.as_view(), name="auth_refresh"),

    # Me + profile
    path("me/", views.me, name="auth_me"),
    path("profile/", views.update_profile, name="auth_update_profile"),

    # Admin role
    path("admin/users/<int:user_id>/role/", views.admin_set_role, name="admin_set_role"),

    # Password reset
    path("forgot-password/", views.forgot_password, name="auth_forgot_password"),
    path("reset-password/", views.reset_password, name="auth_reset_password"),
]
