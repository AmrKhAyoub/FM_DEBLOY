from django import forms
from django.core.exceptions import ValidationError
from .models import ShoppingListItem


class ShoppingListItemForm(forms.ModelForm):

    class Meta:
        model = ShoppingListItem
        fields = ["ingredient", "quantity_needed"]
        widgets = {
            "ingredient": forms.Select(attrs={"class": "form-select"}),
            "quantity_needed": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.25", "min": "0.00"}
            ),
        }

    def clean_quantity_needed(self):
        quantity = self.cleaned_data.get("quantity_needed")
        if quantity is not None and quantity <= 0:
            raise ValidationError("Quantity needed must be greater than zero.")
        return quantity


class ShoppingListQuantityForm(ShoppingListItemForm):

    class Meta(ShoppingListItemForm.Meta):
        fields = ["quantity_needed"]