from django.urls import path
from . import views


app_name = 'recipe_journal'
urlpatterns = [
    path('', views.index_view, name='index'),
    path('recipe/<int:pk>/', views.recipe_detail_view, name="recipe"),
    path('add/', views.add_recipe_view, name='add_recipe'),
    path('recipe/<int:pk>/add-entry/', views.add_entry_view, name="add_entry"),
    path('recipe/<int:pk>/photos/', views.recipe_photos_view, name="recipe_photos"),
    path('recipe/<int:pk>/text/', views.recipe_text_view, name="recipe_text"),
    path('photo/<int:pk>/rotate-right/', views.rotate_right_view, name="rotate_right"),
    path('photo/<int:pk>/rotate-left/', views.rotate_left_view, name="rotate_left"),
]