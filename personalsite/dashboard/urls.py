from django.urls import path

from . import views

app_name = "dashboard"
urlpatterns = [
    path("", views.dash_view, name="dash"),
    path("login-redirect/", views.login_redirect_view, name="login_redirect"),
]
