from datetime import datetime
from django.shortcuts import render

from .models import Location

from .forms import IndexForm


# Create your views here.
def index(request):
    form = IndexForm(request.GET)
    if form.is_valid():
        view_date = form.cleaned_data["view_date"]
        if not view_date:
            locations = []
        else:
            start_ts = datetime(view_date.year, view_date.month, view_date.day, 0, 0, 0)
            end_ts = datetime(
                view_date.year, view_date.month, view_date.day, 23, 59, 59
            )
            locations = list(
                Location.objects.filter(timestamp__range=(start_ts, end_ts))
                .filter(position_accuracy__lte=300)
                .order_by("timestamp")
                .values(
                    "id",
                    "timestamp",
                    "latitude",
                    "longitude",
                    "position_accuracy",
                    "heading",
                    "speed",
                )
            )
    else:
        locations = []
    return render(
        request, "pranav_tracker/index.html", {"form": form, "locations": locations}
    )
