from django.urls import path
from . import views


app_name = "budget"
urlpatterns = [
    path("", views.home_view, name="home"),
    path("discover/", views.discover_view, name="discover"),
    path("discover/msgdrop/", views.discover_msgdrop, name="discover_msgdrop"),
    path("transaction-report/", views.transaction_report, name="trans_report"),
    path("csvdrop/", views.csvdrop, name="csvdrop"),
    path("csvdrop/save/", views.csvdrop_save, name="csvdrop_save"),
]
