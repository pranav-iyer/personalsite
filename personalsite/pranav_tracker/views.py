from datetime import datetime, date
from django.shortcuts import render
from django.http import JsonResponse
from django.utils import timezone
import pandas as pd
import geopandas

from personalsite.pranav_tracker import ranges

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
            locations = get_locations(view_date)
    else:
        locations = []
    return render(
        request, "pranav_tracker/index.html", {"form": form, "locations": locations}
    )


def get_locations(view_date: datetime):
    start_ts = datetime(view_date.year, view_date.month, view_date.day, 0, 0, 0)
    end_ts = datetime(view_date.year, view_date.month, view_date.day, 23, 59, 59)
    return list(
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


def ranges_view(request):
    form = IndexForm(request.GET)
    ranges = []
    if form.is_valid():
        view_date = form.cleaned_data["view_date"]
        if view_date:
            locations = get_locations(view_date)
            if len(locations) > 0:
                ranges = get_ranges(locations, view_date)
    return JsonResponse({"ranges": ranges})


def get_ranges(locations: list, view_date: date):
    df = pd.DataFrame(locations)
    gdf = geopandas.GeoDataFrame(
        df,
        geometry=geopandas.points_from_xy(df.longitude, df.latitude),
        crs="EPSG:4326",
    )
    utm_crs = gdf.estimate_utm_crs()
    gdf = gdf.to_crs(utm_crs)
    rngs = ranges.get_stationary_ranges(gdf)

    # extend ranges to start at midnight and end at either 23:59 or current time
    now = timezone.now()
    if now.date() != view_date:
        now = now.replace(hour=23, minute=59, second=59)

    # replace first start and last end
    rngs[0]["start_time"] = (
        datetime.fromisoformat(rngs[0]["start_time"])
        .replace(hour=0, minute=0, second=0)
        .isoformat()
    )
    rngs[-1]["end_time"] = (
        datetime.fromisoformat(rngs[-1]["end_time"])
        .replace(hour=now.hour, minute=now.minute, second=now.second)
        .isoformat()
    )

    return rngs
