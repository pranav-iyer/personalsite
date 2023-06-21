from django.contrib.auth import views as auth_views
from django.urls import path
from django.views.generic import TemplateView

from . import views as public_views

app_name = "public"

urlpatterns = [
    path("", TemplateView.as_view(template_name="public/index.html"), name="index"),
    path(
        "about/", TemplateView.as_view(template_name="public/about.html"), name="about"
    ),
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="public/login.html"),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("request-account/", public_views.request_account, name="request_account"),
    path("fav-chars/", public_views.fav_chars, name="fav_chars"),
]
