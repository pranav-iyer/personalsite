import os

from celery import Celery
from dotenv import dotenv_values

env_config = dotenv_values("config/.env")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", env_config["DJANGO_SETTINGS_MODULE"])
app = Celery("config")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
