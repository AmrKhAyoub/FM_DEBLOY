from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordChangeForm,
    UserCreationForm,
)

from .models import CustomUser


class BootstrapFormMixin:
    """
    Adds Bootstrap's "form-control" class to every field of a form.

    Django renders plain <input> tags by default, which Bootstrap does not
    style. Instead of repeating the class on every widget, each account form
    inherits this mixin and gets the styling automatically.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")


class CustomUserCreationForm(BootstrapFormMixin, UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        # We only need the basic fields for registration
        fields = ("username", "email")


class CustomUserLoginForm(BootstrapFormMixin, AuthenticationForm):
    pass


class CustomUserUpdateForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = CustomUser
        # Fields the user is allowed to edit. password is not here.
        fields = ("username", "email")


class CustomPasswordChangeForm(BootstrapFormMixin, PasswordChangeForm):
    pass
