from django.urls import path

from . import views

app_name = 'worsst'
urlpatterns = [
    path('', views.index, name='index'),
]