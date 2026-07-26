from django.urls import path
from . import views

app_name = 'shopping_list'

urlpatterns = [
    path('', views.shopping_list, name='shopping_list'),
    path('add/', views.add_item, name='add_item'),
    path('delete/<int:item_id>/', views.delete_item, name='delete_item'),
    path('toggle/<int:item_id>/', views.toggle_purchased, name='toggle_purchased'),
    path('edit/<int:item_id>/', views.edit_item, name='edit_item'),
    path('add-all-missing/<int:recipe_id>/', views.add_all_missing, name='add_all_missing'),
]