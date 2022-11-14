from django.http.response import Http404, HttpResponse
from django.shortcuts import redirect
from django.utils.http import urlencode
from .models import Search
from django.contrib.auth.models import AnonymousUser

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
                f"https://duckduckgo.com/?{urlencode([('q', request.GET['q'])])}"
            )
        else:
            return redirect("https://duckduckgo.com/")
    else:
        raise Http404()
