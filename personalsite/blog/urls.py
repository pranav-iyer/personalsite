from django.urls import path

from . import views

app_name = "blog"
urlpatterns = [
    # path('', views.list_view, name="list"),
    path("", views.BlogListView.as_view(), name="list"),
    path("drafts/", views.BlogDraftsView.as_view(), name="drafts"),
    path("post/add/", views.add_view, name="add"),
    path("post/<int:post_id>/", views.post_view, name="post"),
    path("post/<int:post_id>/unpublish/", views.unpublish_view, name="unpublish"),
    path("post/<int:post_id>/edit/", views.edit_view, name="edit"),
    path("post/<int:post_id>/add_image/", views.add_image_view, name="add_image"),
]
