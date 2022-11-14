from .base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-gpqcuqcef!fru(6b2ca$^n$)5(icd5591qy@h+8tr*2uuqx$qo"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": "personalsite",
        "USER": "personalsiteuser",
        "PASSWORD": "personalsitepwd",
        "HOST": "localhost",
        "PORT": "",
    }
}


REST_FRAMEWORK = {}

STATIC_ROOT = env_config["LOCAL_STATIC_ROOT"]
MEDIA_ROOT = env_config["LOCAL_MEDIA_ROOT"]

# add cors-headers (only in local environment!)
INSTALLED_APPS += ["corsheaders"]
MIDDLEWARE = ["corsheaders.middleware.CorsMiddleware"] + MIDDLEWARE
CORS_ALLOWED_ORIGINS = [
    "http://127.0.0.1:8080",
    "http://0.0.0.0:8080",
    "http://localhost:8080",
]
OPEN_URLS += ["/api-token-auth/"]
OPEN_APPS += ["ingman"]

STD_URLS += ["/media/"]

INGMAN_URL = "http://localhost:8080"
