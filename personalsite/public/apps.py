from django.apps import AppConfig
from django.contrib.auth.signals import user_logged_in


class PublicConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "public"

    def ready(self):
        from .signals import notify_on_login

        user_logged_in.connect(notify_on_login, dispatch_uid="notify_on_login")
