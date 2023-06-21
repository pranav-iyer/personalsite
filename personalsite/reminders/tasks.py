import json

from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMessage
from django_celery_beat.models import ClockedSchedule, PeriodicTask


def schedule_reminder_email(name_for, message, clock_time):
    sched = ClockedSchedule.objects.create(clocked_time=clock_time)
    reminder_number = PeriodicTask.objects.filter(name__icontains=message[:50]).count()
    task = PeriodicTask.objects.create(
        clocked=sched,
        name=f"Send Message [{message[:50]}] ({reminder_number})",
        task="reminders.tasks.send_reminder_email",
        args=json.dumps([name_for, message]),
        one_off=True,
    )
    return task


@shared_task()
def send_reminder_email(name_for, message):
    if name_for == "pranav":
        to_addr = settings.PRANAV_MAIN_EMAIL
    elif name_for == "katey":
        to_addr = settings.KATEY_MAIN_EMAIL
    else:
        raise ValueError("name_for must be one of {'Pranav', 'Katey'}.")

    email = EmailMessage("[pranaviyer.com] Reminder!!!", message, None, [to_addr])
    email.send()
