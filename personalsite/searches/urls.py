from django.urls import path

from . import views

app_name = "searches"
urlpatterns = [
    path("log/", views.log_search_view, name="log"),
    path("shortcut/", views.search_shortcut_view, name="shortcut"),
]
