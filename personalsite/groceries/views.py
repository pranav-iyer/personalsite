from django.contrib import messages
from django.db.models.functions import Chr, Length, Replace, Trim
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.html import format_html
from django.views.generic import ListView
from yesman.views import truncatechars

from .forms import GListForm
from .models import GList


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


def save_glist_from_dash(request, pk):
    if request.method == "POST":
        post_data = request.POST.copy()
        redirect_url = None
        if "submit_save" in post_data:
            post_data.pop("submit_save")
            redirect_url = "dashboard:dash"

        if "submit_edit" in post_data:
            post_data.pop("submit_edit")
            redirect_url = "grocs:edit"

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
        should_complete = False
        if "complete" in post_data:
            should_complete = True
            post_data.pop("complete")

        form = GListForm(post_data, instance=glist)
        if form.is_valid():
            form.save()
            if should_complete:
                glist.completed = timezone.now()
                glist.save()
            return redirect("grocs:edit", glist.id)
        else:
            print(form.errors)
    form = GListForm(instance=glist)
    return render(
        request,
        "groceries/glist_edit.html",
        {
            "form": form,
            "items": glist.items,
            "checked_items": glist.checked_items,
            "unchecked_items": glist.unchecked_items,
        },
    )


def create_glist(request):
    if request.method == "POST":
        form = GListForm(request.POST)
        if form.is_valid():
            glist = form.save()

            return redirect("grocs:edit", glist.id)
    else:
        form = GListForm()
    return render(request, "groceries/glist_create.html", {"form": form})
