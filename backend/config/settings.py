# config/settings.py
from pathlib import Path
from datetime import timedelta
import os

BASE_DIR = Path(__file__).resolve().parent.parent

# =========================================================
# ✅ ENV / SECRET
# =========================================================
# Bonnes pratiques : ne garde pas les secrets en dur en prod
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "django-insecure-dev-only-change-me")
DEBUG = os.getenv("DJANGO_DEBUG", "1") == "1"

ENV = os.getenv("ENV", "dev").lower()  # dev | prod

ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost").split(",")

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173").rstrip("/")

# =========================================================
# ✅ APPS
# =========================================================
INSTALLED_APPS = [
    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Third-party
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "corsheaders",

    # Local apps
    "api",
    "user",
    "vente",
    "client",
    "article",
    "livraison",
    "achats",
    "dashboard",
    "encaissement",
    "configuration",
    "facturation.apps.FacturationConfig",
    "conflivraison",
    "charge",
]

# =========================================================
# ✅ AUTH / USER
# =========================================================
AUTH_USER_MODEL = "user.User"

AUTHENTICATION_BACKENDS = [
    "user.backends.EmailBackend",                 # ✅ login email
    "django.contrib.auth.backends.ModelBackend",  # fallback
]

# =========================================================
# ✅ REST / JWT
# =========================================================
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_PAGINATION_CLASS": "vente.pagination.StandardResultsSetPagination",
    "PAGE_SIZE": 20,
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=int(os.getenv("JWT_ACCESS_MINUTES", "10"))),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=int(os.getenv("JWT_REFRESH_DAYS", "7"))),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
}

# =========================================================
# ✅ MIDDLEWARE
# =========================================================
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",  # ✅ doit être tout en haut
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",

    # ⚠️ CSRF : en API JWT, on garde CSRF actif pour admin + pages Django,
    # mais côté Vue (API), tu utilises JWT => CSRF ne s'applique pas sur Authorization header.
    "django.middleware.csrf.CsrfViewMiddleware",

    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# =========================================================
# ✅ CORS / CSRF (Vue.js)
# =========================================================
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

# Si tu utilises cookies cross-site un jour, active ceci :
# CORS_ALLOW_CREDENTIALS = True

# CSRF trusted origins (utile si tu fais admin via domain)
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

# =========================================================
# ✅ URLS / TEMPLATES / WSGI
# =========================================================
ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# =========================================================
# ✅ DATABASE
# =========================================================
# Dev: sqlite (ok)
# Prod: Postgres (option prête)
DB_ENGINE = os.getenv("DB_ENGINE", "sqlite").lower()

if DB_ENGINE == "postgres":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.getenv("DB_NAME", "mbolafy"),
            "USER": os.getenv("DB_USER", "postgres"),
            "PASSWORD": os.getenv("DB_PASSWORD", ""),
            "HOST": os.getenv("DB_HOST", "127.0.0.1"),
            "PORT": os.getenv("DB_PORT", "5432"),
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# =========================================================
# ✅ PASSWORD VALIDATORS
# =========================================================
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# =========================================================
# ✅ STATIC / MEDIA
# =========================================================
STATIC_URL = "static/"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# =========================================================
# ✅ I18N / TZ
# =========================================================
LANGUAGE_CODE = os.getenv("LANGUAGE_CODE", "fr-fr")
TIME_ZONE = os.getenv("TIME_ZONE", "Indian/Antananarivo")  # ✅ Madagascar (meilleur que UTC pour toi)
USE_I18N = True
USE_TZ = True

# =========================================================
# ✅ EMAIL (IMPORTANT pour forgot password)
# =========================================================
# ✅ En DEV, on veut ZERO SMTP pour éviter WinError 10061
# => Django affiche l'email dans le terminal
if DEBUG or ENV == "dev":
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
    DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "no-reply@mbolafy.local")
else:
    # ✅ Prod SMTP (ex: Gmail / Brevo / Mailgun / Mailtrap)
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    EMAIL_HOST = os.getenv("EMAIL_HOST", "")
    EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
    EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
    EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
    EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "1") == "1"
    EMAIL_USE_SSL = os.getenv("EMAIL_USE_SSL", "0") == "1"
    DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", EMAIL_HOST_USER or "no-reply@example.com")

# =========================================================
# ✅ LOGGING (debug utile)
# =========================================================
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {"class": "logging.StreamHandler"},
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO" if not DEBUG else "DEBUG",
    },
    "loggers": {
        "django.request": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": False,
        },
    },
}
