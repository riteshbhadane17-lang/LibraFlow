"""
LibraFlow Django settings.

Django is used for auth, sessions, admin, templating and URL routing.
Business data (books, members, borrow records, notifications) lives in
MongoDB and is accessed through MongoEngine documents defined in each
app's models.py -- NOT through Django's default ORM. A minimal SQLite
database is kept only for Django's built-in auth/session/admin tables.
"""

import os
from pathlib import Path
from datetime import timedelta
import mongoengine

BASE_DIR = Path(__file__).resolve().parent.parent

# --------------------------------------------------------------------------
# Security
# --------------------------------------------------------------------------
SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "dev-only-secret-key-change-this-in-production-!!!",
)
DEBUG = os.environ.get("DJANGO_DEBUG", "True") == "True"
ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "*").split(",")

# --------------------------------------------------------------------------
# Applications
# --------------------------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # third-party
    "rest_framework",
    "corsheaders",

    # local apps
    "apps.accounts",
    "apps.books",
    "apps.members",
    "apps.borrow",
    "apps.dashboard",
    "apps.api",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "libraflow.urls"

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
                "apps.dashboard.context_processors.site_stats",
            ],
        },
    },
]

WSGI_APPLICATION = "libraflow.wsgi.application"
ASGI_APPLICATION = "libraflow.asgi.application"

# --------------------------------------------------------------------------
# Databases
# --------------------------------------------------------------------------
# Django's relational DB -- only used for auth/session/admin tables.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# MongoDB connection for all library data via MongoEngine.
MONGO_DB_NAME = os.environ.get("MONGO_DB_NAME", "libraflow_db")
MONGO_HOST = os.environ.get("MONGO_HOST", "mongodb://localhost:27017")

mongoengine.connect(
    db=MONGO_DB_NAME,
    host=MONGO_HOST,
    alias="default",
)

# --------------------------------------------------------------------------
# Auth
# --------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 8}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "dashboard:home"
LOGOUT_REDIRECT_URL = "accounts:login"

# --------------------------------------------------------------------------
# I18N
# --------------------------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kolkata"
USE_I18N = True
USE_TZ = True

# --------------------------------------------------------------------------
# Static / media
# --------------------------------------------------------------------------
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --------------------------------------------------------------------------
# REST framework
# --------------------------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.TokenAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticatedOrReadOnly",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 10,
}

CORS_ALLOW_ALL_ORIGINS = DEBUG

# --------------------------------------------------------------------------
# LibraFlow custom settings
# --------------------------------------------------------------------------
LIBRAFLOW = {
    "BORROW_PERIOD_DAYS": 14,          # default loan period
    "OVERDUE_CHECK_INTERVAL_HOURS": 24,  # background thread cadence
    "MAX_BOOKS_PER_MEMBER": 5,
    "FINE_PER_DAY": 5,                 # currency units per day overdue
    "BACKUP_DIR": BASE_DIR / "backups",
    "LOG_DIR": BASE_DIR / "logs",
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": BASE_DIR / "logs" / "libraflow.log",
        },
        "console": {"level": "INFO", "class": "logging.StreamHandler"},
    },
    "root": {"handlers": ["console", "file"], "level": "INFO"},
}
