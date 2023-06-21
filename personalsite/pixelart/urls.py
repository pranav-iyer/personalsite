from django.urls import path

from . import views

app_name = "pixelart"
urlpatterns = [
    path("", views.ArtPieceListView.as_view(), name="list"),
    path("draw/<slug:slug>/", views.draw_view, name="draw"),
    path("demo/", views.demo_view, name="demo"),
    path("save/", views.save_view, name="save"),
    path("download/<slug:slug>", views.image_download_view, name="download"),
    path("editor/", views.editor_view, name="editor"),
    path("zipdrop/", views.zipdrop, name="zipdrop"),
]
