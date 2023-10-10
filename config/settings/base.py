"""
Django settings for personalsite project.

Generated by 'django-admin startproject' using Django 3.2.7.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

import sys
from pathlib import Path

from django.contrib import messages
from dotenv import dotenv_values

env_config = dotenv_values("config/.env")

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR / "personalsite"))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    "groceries.apps.GroceriesConfig",
    "reminders.apps.RemindersConfig",
    "yesman.apps.YesmanConfig",
    "searches.apps.SearchesConfig",
    "kateycareer.apps.KateycareerConfig",
    "public.apps.PublicConfig",
    "pixelart.apps.PixelartConfig",
    "recipe_journal.apps.RecipeJournalConfig",
    "blog.apps.BlogConfig",
    "ingman.apps.IngmanConfig",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.postgres",
    "rest_framework",
    "rest_framework.authtoken",
    "compressor",
    "django_filters",
    "dashboard",
    "budget",
    "pcal",
    "django_celery_beat",
    "til",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "config.middleware.LoginRequiredMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "personalsite/templates"],
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

WSGI_APPLICATION = "config.wsgi.application"


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Europe/Oslo"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "personalsite/static"]
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    "compressor.finders.CompressorFinder",
]

# media files
MEDIA_URL = "/media/"

# sass compiler
COMPRESS_PRECOMPILERS = (("text/x-scss", "django_libsass.SassCompiler"),)

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_URL = "public:login"
LOGIN_REDIRECT_URL = "dashboard:login_redirect"
LOGOUT_REDIRECT_URL = "public:index"
# can manually add in URLs here that should be outside of the login wall
OPEN_URLS = [
    "/search/shortcut/",
    "/pixelart/demo/",
    "/yesman/api/",
    "blog:list",
    "blog:post",
]
OPEN_APPS = ["public"]

# apps and urls that are open to regular users. everything else is by default only open to staff users
STD_URLS = ["dashboard:login_redirect"]
STD_APPS = ["pixelart"]

PIXELART_UPLOAD_DIR = env_config["PIXELART_UPLOAD_DIR"]


# email settings (sends through one of my gmails)
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_HOST_USER = env_config["FROM_EMAIL"]
EMAIL_HOST_PASSWORD = env_config["FROM_EMAIL_PASSWD"]
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = '"Pranav Iyer" <mail@pranaviyer.com>'

PRANAV_MAIN_EMAIL = env_config["PRANAV_MAIN_EMAIL"]
KATEY_MAIN_EMAIL = env_config["KATEY_MAIN_EMAIL"]

# celery settings
CELERY_BROKER_URL = f"redis://:{env_config['REDIS_PASSWD']}@localhost:6379"
CELERY_RESULT_BACKEND = f"redis://:{env_config['REDIS_PASSWD']}@localhost:6379"

CUSTOM_MESSAGE_LEVELS = {"ALERT": 35}
MESSAGE_TAGS = {
    messages.INFO: "bg-info icon-info-circle",
    messages.SUCCESS: "bg-success icon-check-lg",
    messages.WARNING: "bg-warning icon-exclamation-diamond",
    messages.ERROR: "bg-danger icon-exclamation-octagon-fill",
    CUSTOM_MESSAGE_LEVELS["ALERT"]: "bg-secondary icon-bell-fill",
}

# telegram settings
TELEGRAM_BOT_KEY = env_config["TELEGRAM_BOT_KEY"]
TELEGRAM_USER_ID = env_config["TELEGRAM_USER_ID"]
