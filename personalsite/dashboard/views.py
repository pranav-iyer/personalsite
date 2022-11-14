from django.shortcuts import render, redirect
from django.db.models.functions import Length, Replace, Trim, Chr
from reminders.scheduling import TIMING_CHOICES
from yesman.models import YesItem
from groceries.models import GList
from django.contrib import messages
from django.utils.html import format_html

# Create your views here.
NUM_YESES_TO_SHOW = 7
NUM_GLISTS_TO_SHOW = 2


def dash_view(request):
    context = {}

    context["yeses"] = YesItem.objects.filter(completed__isnull=True)[
        :NUM_YESES_TO_SHOW
    ]
    context["num_extra_yeses"] = max(
        YesItem.objects.filter(completed__isnull=True).count() - NUM_YESES_TO_SHOW, 0
    )

    context["glists"] = (
        GList.objects.filter(completed__isnull=True)
        .order_by("-updated")
        .annotate(
            num_items=Length(Trim("contents"))
            - Length(Replace(Trim("contents"), Chr(ord("\n"))))
            + 1
        )[:NUM_GLISTS_TO_SHOW]
    )
    context["num_extra_glists"] = max(
        GList.objects.filter(completed__isnull=True).count() - NUM_GLISTS_TO_SHOW, 0
    )

    # no need for custom times in the quick reminder shortcut
    context["reminder_timing_choices"] = [x for x in TIMING_CHOICES if x[0] != "custom"]

    return render(request, "dashboard/dashboard.html", context)


def login_redirect_view(request):
    if request.user.is_staff:
        return redirect("dashboard:dash")
    else:
        return redirect("pixelart:list")
