from django.urls import path
from . import views


app_name = 'yesman'
urlpatterns = [
    path('', views.YesListActiveView.as_view(), name='list'),
    path('create/', views.YesListCreateView.as_view(), name='create'),
    path('complete/<int:pk>/', views.complete_yesitem, name='complete'),
    path('remind/<int:pk>/', views.remind_yesitem, name='remind'),
]