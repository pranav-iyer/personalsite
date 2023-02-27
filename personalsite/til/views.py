from django.shortcuts import redirect, render
from django.views.generic.list import ListView

from .forms import TidbitForm
from .models import Tidbit


# Create your views here.
class IndexView(ListView):
    paginate_by = 10
    model = Tidbit
    template_name = "til/index.html"
    ordering = "-created"
    context_object_name = "tidbits"


def add_view(request):
    if request.method == "POST":
        form = TidbitForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("til:index")
    else:
        form = TidbitForm()
    return render(request, "til/add.html", {"form": form})
