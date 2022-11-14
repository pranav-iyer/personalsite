from django.urls import path
from . import views


app_name = "pcal"
urlpatterns = [
    path("", views.home_view, name="home"),
    path("week/<int:year>/<int:month>/<int:day>/", views.week_view, name="week"),
    path("event/<int:pk>/", views.event_detail, name="event"),
    path("event/add/", views.add_event, name="add_event"),
]
