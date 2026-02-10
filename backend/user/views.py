# user/views.py
from __future__ import annotations

from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status

from rest_framework_simplejwt.tokens import RefreshToken, TokenError

from .serializers import (
    RegisterSerializer,
    MeSerializer,
    UpdateProfileSerializer,
    AdminSetRoleSerializer,
)

User = get_user_model()


@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    return Response(
        {"message": "User created", "id": user.id},
        status=status.HTTP_201_CREATED
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    """
    ✅ Login avec email + password
    Retourne access + refresh token JWT
    """
    email = (request.data.get("email") or "").strip().lower()
    password = request.data.get("password")

    if not email or not password:
        return Response(
            {"detail": "Email et mot de passe requis."},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = authenticate(request, email=email, password=password)

    if not user:
        return Response(
            {"detail": "Identifiants invalides."},
            status=status.HTTP_401_UNAUTHORIZED
        )

    if not user.is_active:
        return Response(
            {"detail": "Ce compte est désactivé."},
            status=status.HTTP_403_FORBIDDEN
        )

    refresh = RefreshToken.for_user(user)

    return Response(
        {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": MeSerializer(user, context={"request": request}).data,
        },
        status=status.HTTP_200_OK
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me(request):
    return Response(
        MeSerializer(request.user, context={"request": request}).data,
        status=status.HTTP_200_OK
    )


@api_view(["PUT", "PATCH"])
@permission_classes([IsAuthenticated])
def update_profile(request):
    """
    ✅ Modifier son profil
    - role non modifiable ici
    """
    serializer = UpdateProfileSerializer(
        request.user,
        data=request.data,
        partial=(request.method == "PATCH"),
        context={"request": request},
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(
        {"message": "Profil mis à jour", "user": MeSerializer(request.user, context={"request": request}).data},
        status=status.HTTP_200_OK
    )


@api_view(["PATCH"])
@permission_classes([IsAdminUser])
def admin_set_role(request, user_id: int):
    """
    ✅ Seul l'admin peut changer le role d'un user
    """
    try:
        target = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return Response({"detail": "Utilisateur introuvable"}, status=status.HTTP_404_NOT_FOUND)

    serializer = AdminSetRoleSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    target.role = serializer.validated_data["role"]
    target.save(update_fields=["role"])

    return Response(
        {"message": "Rôle mis à jour", "user": MeSerializer(target, context={"request": request}).data},
        status=status.HTTP_200_OK
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def forgot_password(request):
    email = (request.data.get("email") or "").strip().lower()
    if not email:
        return Response({"email": ["L'email est obligatoire."]}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(email__iexact=email)
    except User.DoesNotExist:
        return Response({"message": "If the email exists, a reset link was sent."}, status=status.HTTP_200_OK)

    token = default_token_generator.make_token(user)
    uid = str(user.pk)

    frontend_url = getattr(settings, "FRONTEND_URL", "http://localhost:5173")
    reset_link = f"{frontend_url}/reset-password?uid={uid}&token={token}"

    if getattr(settings, "EMAIL_HOST", None):
        send_mail(
            "Password reset",
            f"Use this link to reset your password: {reset_link}",
            getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@example.com"),
            [user.email],
            fail_silently=True,
        )

    return Response(
        {"message": "If the email exists, a reset link was sent.", "reset_link_dev": reset_link},
        status=status.HTTP_200_OK
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def reset_password(request):
    uid = request.data.get("uid")
    token = request.data.get("token")
    new_password = request.data.get("new_password")

    if not uid or not token or not new_password:
        return Response({"detail": "uid, token, new_password are required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(pk=uid)
    except User.DoesNotExist:
        return Response({"detail": "Invalid link"}, status=status.HTTP_400_BAD_REQUEST)

    if not default_token_generator.check_token(user, token):
        return Response({"detail": "Invalid or expired token"}, status=status.HTTP_400_BAD_REQUEST)

    user.set_password(new_password)
    user.save()
    return Response({"message": "Password updated"}, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout(request):
    """
    ✅ Déconnexion utilisateur:
    - blacklist le refresh token (si fourni)
    """
    refresh_token = request.data.get("refresh")

    if not refresh_token:
        # On autorise quand même la déconnexion côté frontend (suppression storage)
        return Response({"message": "Déconnexion réussie (client)."}, status=status.HTTP_200_OK)

    try:
        token = RefreshToken(refresh_token)
        token.blacklist()
    except TokenError:
        return Response({"detail": "Refresh token invalide ou expiré."}, status=status.HTTP_400_BAD_REQUEST)
    except Exception:
        return Response({"detail": "Erreur lors de la déconnexion."}, status=status.HTTP_400_BAD_REQUEST)

    return Response({"message": "Déconnexion réussie."}, status=status.HTTP_200_OK)
