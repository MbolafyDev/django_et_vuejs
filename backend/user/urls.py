# user/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("register/", views.register, name="register"),
    path("login/", views.login, name="login"),  # ✅ email login
    path("logout/", views.logout, name="logout"),
    path("me/", views.me, name="me"),
    path("profile/", views.update_profile, name="update_profile"),  # ✅ modifier profil
    path("admin/users/<int:user_id>/role/", views.admin_set_role, name="admin_set_role"),  # ✅ admin role
    path("forgot-password/", views.forgot_password, name="forgot_password"),
    path("reset-password/", views.reset_password, name="reset_password"),
]
