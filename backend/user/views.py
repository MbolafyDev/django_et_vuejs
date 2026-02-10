from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import RegisterSerializer

from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

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
    Login utilisateur avec username + password
    Retourne access + refresh token JWT
    """
    username = request.data.get("username")
    password = request.data.get("password")

    if not username or not password:
        return Response(
            {"detail": "Username et mot de passe requis."},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = authenticate(username=username, password=password)

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
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
            },
        },
        status=status.HTTP_200_OK
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me(request):
    u = request.user
    return Response(
        {
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "first_name": u.first_name,
            "last_name": u.last_name,
        },
        status=status.HTTP_200_OK
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def forgot_password(request):
    email = (request.data.get("email") or "").strip().lower()
    if not email:
        return Response(
            {"email": ["L'email est obligatoire."]},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        user = User.objects.get(email__iexact=email)
    except User.DoesNotExist:
        # sécurité: ne pas révéler si l'email existe
        return Response(
            {"message": "If the email exists, a reset link was sent."},
            status=status.HTTP_200_OK
        )

    token = default_token_generator.make_token(user)
    uid = str(user.pk)

    # lien front (dev)
    frontend_url = getattr(settings, "FRONTEND_URL", "http://localhost:5173")
    reset_link = f"{frontend_url}/reset-password?uid={uid}&token={token}"

    # email si configuré
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
        return Response(
            {"detail": "uid, token, new_password are required"},
            status=status.HTTP_400_BAD_REQUEST
        )

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
    Déconnexion utilisateur (blacklist du refresh token)
    """
    try:
        refresh_token = request.data.get("refresh")
        token = RefreshToken(refresh_token)
        token.blacklist()
    except Exception:
        return Response(
            {"detail": "Token invalide ou manquant."},
            status=status.HTTP_400_BAD_REQUEST
        )

    return Response(
        {"message": "Déconnexion réussie."},
        status=status.HTTP_200_OK
    )
