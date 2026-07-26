from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordChangeForm,
    UserCreationForm,
)

from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        # We only need the basic fields for registration
        fields = ("username", "email")


class CustomUserLoginForm(AuthenticationForm):
    pass


class CustomUserUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        # Fields the user is allowed to edit. Password is not here.
        fields = ("username", "email")


class CustomPasswordChangeForm(PasswordChangeForm):
    pass
