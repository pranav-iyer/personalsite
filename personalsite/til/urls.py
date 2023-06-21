from django.urls import path

from . import views

app_name = "til"
urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("add/", views.add_view, name="add"),
]
