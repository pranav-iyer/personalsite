from django.contrib.auth.models import AnonymousUser
from django.http.response import Http404, HttpResponse
from django.shortcuts import redirect, render
from django.utils.http import urlencode

from .models import Search


# Create your views here.
def log_search_view(request):
    if request.method == "GET":
        raise Http404()
    elif request.method == "POST":
        if not isinstance(request.user, AnonymousUser) and request.user.is_staff:
            Search.objects.create(text=request.POST["searchText"], user=request.user)
        else:
            Search.objects.create(text=request.POST["searchText"])
        return HttpResponse("logged.")
    else:
        raise Http404()


# http://127.0.0.1:8000/search/shortcut/?q=pranav dlk//js\\adfsa()!**^%&$;
def search_shortcut_view(request):
    if request.method == "GET":
        if "q" in request.GET:
            if not isinstance(request.user, AnonymousUser) and request.user.is_staff:
                Search.objects.create(text=request.GET["q"], user=request.user)
            else:
                Search.objects.create(text=request.GET["q"])
            return redirect(
                f"https://ecosia.org/search?{urlencode([('q', request.GET['q'])])}"
            )
        else:
            return redirect("https://ecosia.org/")
    else:
        raise Http404()


def browse_searches_view(request):
    if request.method == "GET":
        q = request.GET.get("q")
        if q:
            searches = Search.objects.filter(text__icontains=q).order_by("-timestamp")
        else:
            searches = Search.objects.order_by("-timestamp")[:10]

    return render(request, "searches/browse.html", {"searches": searches})
