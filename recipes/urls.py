from django.urls import path
from . import views

app_name = 'recipes'
urlpatterns = [
    path('', views.recipe_list, name='recipe_list'),
    path('<int:recipe_id>/', views.recipe_detail, name='recipe_detail'),
    path('recommended/', views.recommended_recipes, name='recommended_recipes'),
    path('live-search/', views.live_search, name='live_search'),
    path("favorites/", views.favorite_recipes,  name="favorite_recipes"),
    path("<int:recipe_id>/favorite/", views.toggle_favorite, name="toggle_favorite"),
    path("favorites/remove/<int:recipe_id>/", views.remove_favorite,name="remove_favorite",),
    path("favorites/clear/", views.clear_favorites,name="clear_favorites",),
    path('ingredient-search/', views.ingredient_search, name='ingredient_search'),
    ]