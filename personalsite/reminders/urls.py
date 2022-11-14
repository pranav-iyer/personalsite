from django.urls import path
from . import views


app_name = 'reminders'
urlpatterns = [
    path('', views.create_reminder_view, name='create'),
    path('success', views.success_view, name='success')
]