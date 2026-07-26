from django.urls import path

from . import views

app_name = "pantry"

urlpatterns = [
    path("", views.pantry_list_view, name="list"),
    path("add/", views.pantry_add_view, name="add"),
    path("update/<int:pk>/", views.pantry_update_view, name="update"),
    path("delete/<int:pk>/", views.pantry_delete_view, name="delete"),
]
