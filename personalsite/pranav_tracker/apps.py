from django.apps import AppConfig
from compressor import signals

from .signals import post_compress_handler


class PranavTrackerConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "pranav_tracker"

    def ready(self):
        signals.post_compress.connect(post_compress_handler)
