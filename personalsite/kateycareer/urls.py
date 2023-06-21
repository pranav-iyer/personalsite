from django.urls import path

from . import views

app_name = "ktc"
urlpatterns = [
    path("", views.index_view, name="index"),
    path("add/", views.AddView.as_view(), name="add"),
    path("work-checklist/", views.work_checklist, name="work_checklist"),
]
