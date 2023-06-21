from django.conf import settings
from django.core.mail import EmailMessage


def notify_on_login(sender, **kwargs):
    user = kwargs.get("user")
    request = kwargs.get("request")
    if user is not None and request is not None:
        header_string = ""
        for key in request.headers:
            header_string += f"\t{key}: {request.headers[key]}\n"
        message_body = f"User {user.username} ({user.first_name} {user.last_name}) just successfully logged in.\n\nDetails:\nIP Address - {request.META['REMOTE_ADDR']}\nHostname - {request.META['REMOTE_ADDR']}\nHeaders \n{header_string}"
        if not settings.DEBUG:
            msg = EmailMessage(
                "[pranaviyer.com] Security Alert",
                message_body,
                None,
                [settings.PRANAV_MAIN_EMAIL],
            )
            msg.send()
        else:
            print("User logged in, sending email:")
            print(message_body)
