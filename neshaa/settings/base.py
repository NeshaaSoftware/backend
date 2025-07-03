import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = os.getenv("SECRET_KEY", "tF7EpQUgVm4os%ArQyL13I+g*V8JV&dvd11#c50#ni3vDe&bsS")
DEBUG = False
ALLOWED_HOSTS = []

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_jalali",
    "django_extensions",
    # Local apps
    "commons",
    "users",
    "courses",
    "financials",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "neshaa.urls"

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

WSGI_APPLICATION = "neshaa.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
USE_I18N = True
USE_TZ = True
TIME_ZONE = "Asia/Tehran"

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

# Media files
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Custom User Model
AUTH_USER_MODEL = "users.User"

# Logging configuration
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": BASE_DIR / "django.log",
            "formatter": "verbose",
        },
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    },
    "root": {
        "handlers": ["console", "file"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },
        "django.db.backends": {
            "handlers": ["console", "file"],
            "level": "WARNING",
            "propagate": False,
        },
        "audit": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },
    },
}


JALALI_SETTINGS = {
    # JavaScript static files for the admin Jalali date widget
    "ADMIN_JS_STATIC_FILES": [
        "admin/jquery.ui.datepicker.jalali/scripts/jquery-1.10.2.min.js",
        "admin/jquery.ui.datepicker.jalali/scripts/jquery.ui.core.js",
        "admin/jquery.ui.datepicker.jalali/scripts/jquery.ui.datepicker-cc.js",
        "admin/jquery.ui.datepicker.jalali/scripts/calendar.all.js",
        "admin/jquery.ui.datepicker.jalali/scripts/calendar.js",
        "admin/jquery.ui.datepicker.jalali/scripts/jquery.ui.datepicker-cc-fa.js",
        "admin/main.js",
    ],
    # CSS static files for the admin Jalali date widget
    "ADMIN_CSS_STATIC_FILES": {
        "all": [
            "admin/jquery.ui.datepicker.jalali/themes/base/jquery-ui.min.css",
            "admin/css/main.css",
        ]
    },
}

SHELL_PLUS = "ipython"  # Or "bpython" or "ptpython"
SHELL_PLUS_PRINT_SQL = True  # To print SQL queries executed by Django ORM

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Security settings for production
# SECURE_HSTS_SECONDS = 31536000  # 1 year
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True
# SECURE_HSTS_PRELOAD = True
# SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
