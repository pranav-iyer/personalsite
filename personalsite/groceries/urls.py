from django.urls import path
from . import views


app_name = 'grocs'
urlpatterns = [
    path("glists/all/", views.GListAllView.as_view(), name="list_all"),
    path("glists/active/", views.GListActiveView.as_view(), name="list_active"),
    path("glist/<int:pk>/edit/", views.edit_glist, name="edit"),
    path("glist/<int:pk>/shopping/", views.shopping, name="shopping"),
    path("glist/<int:pk>/delete/", views.delete_list, name="delete"),
    path("glist/<int:pk>/save-from-dash/", views.save_glist_from_dash, name="save_glist_from_dash"),
    path("glist/create/", views.create_glist, name="create"),
]