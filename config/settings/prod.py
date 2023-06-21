from dotenv import dotenv_values

from .base import *

# env_config = dotenv_values("config/.env")

DEBUG = False
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True

SECRET_KEY = env_config.get("DJANGO_SECRET_KEY", "")

ALLOWED_HOSTS = ["104.248.10.24", "localhost", "pranaviyer.com"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": "gman",
        "USER": "gmanuser",
        "PASSWORD": env_config.get("POSTGRES_PASSWORD", ""),
        "HOST": "localhost",
        "PORT": "",
    }
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "root": {"level": "INFO", "handlers": ["file"]},
    "handlers": {
        "file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": env_config.get("DJANGO_LOG_LOCATION", ""),
            "formatter": "app",
        },
    },
    "loggers": {
        "django": {"handlers": ["file"], "level": "INFO", "propagate": True},
    },
    "formatters": {
        "app": {
            "format": (
                "%(asctime)s [%(levelname)-8s] " "(%(module)s.%(funcName)s) %(message)s"
            ),
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
}

STATIC_ROOT = env_config.get("DJANGO_STATIC_LOCATION", "")
MEDIA_ROOT = env_config.get("DJANGO_MEDIA_LOCATION", "")


REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        # 'rest_framework.authentication.TokenAuthentication',
        "rest_framework.authentication.SessionAuthentication",
    ],
}

INGMAN_URL = "/ingman-app/"
