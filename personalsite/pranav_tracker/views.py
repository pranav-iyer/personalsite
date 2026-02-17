from datetime import datetime
from django.shortcuts import render
from django.http import JsonResponse
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
            ranges = []
        else:
            locations = get_locations(view_date)
            ranges = get_ranges(locations)
    else:
        locations = []
        ranges = []
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
                ranges = get_ranges(locations)
    return JsonResponse({"ranges": ranges})


def get_ranges(locations: list):
    df = pd.DataFrame(locations)
    gdf = geopandas.GeoDataFrame(
        df,
        geometry=geopandas.points_from_xy(df.longitude, df.latitude),
        crs="EPSG:4326",
    )
    utm_crs = gdf.estimate_utm_crs()
    gdf = gdf.to_crs(utm_crs)
    return ranges.get_stationary_ranges(gdf)
