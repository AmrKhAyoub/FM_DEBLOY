from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    # Authentication
    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", views.CustomLoginView.as_view(), name="login"),
    # Using Django's built-in LogoutView directly here
    path("logout/", LogoutView.as_view(next_page="accounts:login"), name="logout"),

    # Profile management
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path("profile/edit/", views.ProfileUpdateView.as_view(), name="edit_profile"),
    path(
        "profile/password/",
        views.CustomPasswordChangeView.as_view(),
        name="change_password",
    ),
    path("profile/delete/", views.AccountDeleteView.as_view(), name="delete_account"),
]
