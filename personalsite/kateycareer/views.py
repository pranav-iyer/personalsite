from django.http.response import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from .models import CareerInfo
from django.views.generic import CreateView


# Create your views here.
def index_view(request):
    return HttpResponse("hello!")


def work_checklist(request):
    return render(request, "kateycareer/work_checklist.html")


# def add_view(request):
#     if request.method == "POST":
#         form = CareerInfoForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return redirect("dash")
#     else:
#         form = CareerInfoForm()
#     return render(request, "kateycareer/add.html", {'form': form})


class AddView(CreateView):
    model = CareerInfo
    fields = ["job_title"]
    template_name = "kateycareer/add.html"
    success_url = reverse_lazy("dashboard:dash")
