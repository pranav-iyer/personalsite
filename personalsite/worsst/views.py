from django.db.models import F
from django.shortcuts import render

from .models import Entry, EntryContent, EntryImage, Feed, FeedGroup


# Create your views here.
def index(request):
    context = {}
    context["entries"] = Entry.objects.order_by("-updated").order_by(
        F("published").desc(nulls_last=True)
    )[:50]
    return render(request, "worsst/index.html", context)
