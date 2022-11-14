from curses.ascii import HT
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView
from django.db.models import Value as V
from django.db.models.functions import Chr, Length, Trim, Replace
from django.utils import timezone
from django.contrib import messages
from django.utils.html import format_html

from yesman.views import truncatechars
from .models import GList
from .forms import GListForm


class GListListView(ListView):
    model = GList
    paginate_by = 7
    context_object_name = "glists"
    template_name = "groceries/glist_list.html"


class GListActiveView(GListListView):
    def get_queryset(self):
        return (
            GList.objects.filter(completed__isnull=True)
            .order_by("-updated")
            .annotate(
                num_items=Length(Trim("contents"))
                - Length(Replace(Trim("contents"), Chr(ord("\n"))))
                + 1
            )
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["viewing"] = "active"
        return ctx


class GListAllView(GListListView):
    def get_queryset(self):
        return GList.objects.order_by("-updated").annotate(
            num_items=Length(Trim("contents"))
            - Length(Replace(Trim("contents"), Chr(ord("\n"))))
            + 1
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["viewing"] = "all"
        return ctx


def delete_list(request, pk):
    glist = get_object_or_404(GList, pk=pk)
    if request.method == "POST":
        glist.delete()
        return redirect("grocs:list_active")
    raise Http404()


def shopping(request, pk):
    glist = get_object_or_404(GList, pk=pk)
    if request.method == "POST":
        if "done_list" in request.POST:
            glist.completed = timezone.now()
            glist.save()

            return redirect("grocs:list_all")
    items = glist.contents.strip().split("\n")
    return render(request, "groceries/shopping.html", {"glist": glist, "items": items})


def save_glist_from_dash(request, pk):
    if request.method == "POST":
        post_data = request.POST.copy()
        redirect_url = None
        if "submit_save" in post_data:
            post_data.pop("submit_save")
            redirect_url = "dashboard:dash"

        if "submit_shopping" in post_data:
            post_data.pop("submit_shopping")
            redirect_url = "grocs:shopping"

        glist = get_object_or_404(GList, pk=pk)
        form = GListForm(post_data, instance=glist)

        if form.is_valid():
            form.save()

            if redirect_url == "dashboard:dash":
                messages.info(
                    request,
                    format_html(
                        "List <b>{}</b> saved.",
                        f'"{truncatechars(glist.title, 30)}"',
                    ),
                )
                return redirect(redirect_url)
            else:
                return redirect(redirect_url, glist.pk)

    raise Http404()


def edit_glist(request, pk):
    glist = get_object_or_404(GList, pk=pk)
    if request.method == "POST":
        post_data = request.POST.copy()
        redirect_url = None
        if "submit_save" in post_data:
            post_data.pop("submit_save")
            redirect_url = "grocs:edit"

        if "submit_shopping" in post_data:
            post_data.pop("submit_shopping")
            redirect_url = "grocs:shopping"

        form = GListForm(post_data, instance=glist)
        if form.is_valid():
            form.save()

            return redirect(redirect_url, pk)
    else:
        form = GListForm(instance=glist)
    return render(request, "groceries/glist_edit.html", {"form": form})


def create_glist(request):
    if request.method == "POST":
        form = GListForm(request.POST)
        if form.is_valid():
            form.save()

            return redirect("grocs:list_active")
    else:
        form = GListForm()
    return render(request, "groceries/glist_create.html", {"form": form})
