from django.conf import settings
from reminders.tasks import send_telegram_message


def notify_on_login(sender, **kwargs):
    user = kwargs.get("user")
    request = kwargs.get("request")
    if user is not None and request is not None:
        header_string = ""
        for key in ["User-Agent", "Host", "Referer", "Origin"]:
            header_string += f"\t{key}: {request.headers.get(key, '-')}\n"
        message_body = f"User {user.username} ({user.first_name} {user.last_name}) just successfully logged in.\n\nDetails:\nIP Address - {request.META['REMOTE_ADDR']}\nHostname - {request.META['REMOTE_ADDR']}\nHeaders \n{header_string}"
        if not settings.DEBUG:
            send_telegram_message(message_body)
        else:
            print("User logged in, sending message:")
            print(message_body)
