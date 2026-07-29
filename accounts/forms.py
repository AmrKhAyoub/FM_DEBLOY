from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordChangeForm,
    UserCreationForm,
)

from .models import CustomUser


class BootstrapFormMixin:
   
    # Automatically apply Bootstrap styling to all form fields
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")


# Form used for user registration
class CustomUserCreationForm(BootstrapFormMixin, UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        # We only need the basic fields for registration
        fields = ("username", "email")


# Login form
class CustomUserLoginForm(BootstrapFormMixin, AuthenticationForm):
    pass

# Form for updating profile information
class CustomUserUpdateForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = CustomUser
        # Fields the user is allowed to edit. password is not here.
        fields = ("username", "email")

# Password change form
class CustomPasswordChangeForm(BootstrapFormMixin, PasswordChangeForm):
    pass
