from django.urls import path
from . import views

app_name = 'recipes'
urlpatterns = [
    path('', views.recipe_list, name='recipe_list'),
    path('<int:recipe_id>/', views.recipe_detail, name='recipe_detail'),
    path('recommended/', views.recommended_recipes, name='recommended_recipes'),
    path('live-search/', views.live_search, name='live_search'),
]