```python
"""
Django settings for realestate project.

Configured for local development and Render production deployment.
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


# ==============================================================================
# Environment Variables
# ==============================================================================

try:
    from dotenv import load_dotenv
    load_dotenv(BASE_DIR / ".env")
except ImportError:
    pass


# ==============================================================================
# Security
# ==============================================================================

DEBUG = os.environ.get("DEBUG", "False").lower() in (
    "true",
    "1",
    "t",
    "yes",
)

SECRET_KEY = os.environ.get("SECRET_KEY")

if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY = (
            "django-insecure-dev-key-w6rm%l&xim0ivll-li$u6fg8)6k8-$7uar^f#33ht5sutw8e!..."
        )
    else:
        raise ValueError(
            "SECRET_KEY environment variable is missing. "
            "Set SECRET_KEY in Render Environment Variables."
        )


# ==============================================================================
# Hosts
# ==============================================================================

# Your Render domain
ALLOWED_HOSTS = [
    "real-estate-django-web-app.onrender.com",
    "localhost",
    "127.0.0.1",
]


# ==============================================================================
# CSRF
# ==============================================================================

CSRF_TRUSTED_ORIGINS = [
    "https://real-estate-django-web-app.onrender.com",
]


# ==============================================================================
# Applications
# ==============================================================================

INSTALLED_APPS = [
    "pages.apps.PagesConfig",
    "listings.apps.ListingsConfig",
    "accounts.apps.AccountsConfig",
    "contacts.apps.ContactsConfig",
    "realtors.apps.RealtorsConfig",

    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
]


# ==============================================================================
# Middleware
# ==============================================================================

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",

    "whitenoise.middleware.WhiteNoiseMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# ==============================================================================
# URL / WSGI
# ==============================================================================

ROOT_URLCONF = "realestate.urls"

WSGI_APPLICATION = "realestate.wsgi.application"


# ==============================================================================
# Templates
# ==============================================================================

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


# ==============================================================================
# Database
# ==============================================================================

try:
    import dj_database_url

    DATABASE_URL = os.environ.get("DATABASE_URL")

    if DATABASE_URL:
        DATABASES = {
            "default": dj_database_url.config(
                default=DATABASE_URL,
                conn_max_age=600,
                conn_health_checks=True,
            )
        }
    else:
        DATABASES = {
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": BASE_DIR / "db.sqlite3",
            }
        }

except ImportError:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }


# ==============================================================================
# Password Validation
# ==============================================================================

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "UserAttributeSimilarityValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "MinimumLengthValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "CommonPasswordValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "NumericPasswordValidator"
        ),
    },
]


# ==============================================================================
# Internationalization
# ==============================================================================

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# ==============================================================================
# Default Primary Key
# ==============================================================================

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"


# ==============================================================================
# Static Files / WhiteNoise
# ==============================================================================

STATIC_URL = "/static/"

STATIC_ROOT = BASE_DIR / "staticfiles"

STATICFILES_DIRS = [
    BASE_DIR / "static",
]

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}


# ==============================================================================
# Media / Uploaded Property Images
# ==============================================================================

MEDIA_URL = "/media/"

MEDIA_ROOT = BASE_DIR / "media"


# ==============================================================================
# Messages
# ==============================================================================

from django.contrib.messages import constants as messages

MESSAGE_TAGS = {
    messages.ERROR: "danger",
}


# ==============================================================================
# Production Security
# ==============================================================================

if not DEBUG:

    # Render sits behind a reverse proxy.
    SECURE_PROXY_SSL_HEADER = (
        "HTTP_X_FORWARDED_PROTO",
        "https",
    )

    # Redirect HTTP → HTTPS
    SECURE_SSL_REDIRECT = True

    # Secure cookies
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

    # HSTS
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

    # Security headers
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True

    X_FRAME_OPTIONS = "DENY"
```
