from django.urls import path
from . import views

urlpatterns = [
    path('', views.shopping_list, name='shopping_list'),
    path('add/', views.add_item, name='add_item'),
    path('add-from-recipe/', views.add_from_recipe, name='add_from_recipe'),
    path('delete/<int:item_id>/', views.delete_item, name='delete_item'),
    path('toggle/<int:item_id>/', views.toggle_purchased, name='toggle_purchased'),
    path('edit/<int:item_id>/', views.edit_item, name='edit_item'),
    
]