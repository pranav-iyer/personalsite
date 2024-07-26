from datetime import datetime
from django.shortcuts import render

from .models import Location

from .forms import IndexForm


# Create your views here.
def index(request):
    form = IndexForm(request.GET)
    if form.is_valid():
        start_date = form.cleaned_data["start_date"]
        end_date = form.cleaned_data["end_date"]
        if not start_date or not end_date:
            locations = []
        else:
            start_ts = datetime(
                start_date.year, start_date.month, start_date.day, 0, 0, 0
            )
            end_ts = datetime(end_date.year, end_date.month, end_date.day, 23, 59, 59)
            locations = list(
                Location.objects.filter(timestamp__range=(start_ts, end_ts))
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
    print(locations)
    return render(
        request, "pranav_tracker/index.html", {"form": form, "locations": locations}
    )
