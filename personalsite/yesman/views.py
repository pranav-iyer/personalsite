from asyncio import format_helpers
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.views import generic
from django.utils import timezone
from django.utils.html import format_html
from django.urls import reverse_lazy
import pytz
from datetime import timedelta

from django.contrib import messages
from django.conf import settings

from reminders.tasks import send_reminder_email, schedule_reminder_email
from reminders.scheduling import TIMING_CHOICES, get_eta
from .models import YesItem

# Create your views here.
class YesListActiveView(generic.ListView):
    model = YesItem
    template_name = "yesman/yeslist.html"
    context_object_name = "yeslist"

    def get_queryset(self):
        return YesItem.objects.filter(completed__isnull=True)


class YesListCreateView(generic.CreateView):
    model = YesItem
    fields = ["info"]
    template_name = "yesman/yescreate.html"
    success_url = reverse_lazy("dashboard:dash")


def complete_yesitem(request, pk):
    yesitem = get_object_or_404(YesItem, pk=pk)
    yesitem.completed = timezone.now()
    yesitem.save()

    messages.success(
        request,
        format_html(
            'Task <b>"{}"</b> successfully completed!', truncatechars(yesitem.info, 30)
        ),
    )

    return redirect("dashboard:dash")


def truncatechars(string, length):
    if len(string) <= length:
        return string
    else:
        return string[: length - 1] + "…"


def remind_yesitem(request, pk):
    yesitem = get_object_or_404(YesItem, pk=pk)

    if request.method != "GET" or "time_code" not in request.GET:
        raise Http404()

    now = timezone.now()
    task_eta = get_eta(request.GET["time_code"], request.GET.get("custom_time"))

    # send_reminder_email.apply_async(
    #     args=("pranav", f"To-Do: {yesitem.info}"),
    #     eta=task_eta,
    # )
    schedule_reminder_email("pranav", f"To-Do: {yesitem.info}", task_eta)

    date_string = ""
    if task_eta.day == now.day:
        date_string = "today"
    elif task_eta.day - now.day == 1:
        date_string = "tomorrow"
    else:
        date_string = "on " + task_eta.strftime("%a, %b %d")

    messages.add_message(
        request,
        settings.CUSTOM_MESSAGE_LEVELS["ALERT"],
        format_html(
            "Reminder created for task <b>{}</b> at <b>{}</b> {}.",
            f'"{truncatechars(yesitem.info, 30)}"',
            task_eta.strftime("%I:%M%p").lower(),
            date_string,
        ),
    )
    return redirect("dashboard:dash")
