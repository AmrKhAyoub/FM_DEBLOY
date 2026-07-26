from django import forms

from .models import PantryItem


class PantryItemForm(forms.ModelForm):
    class Meta:
        model = PantryItem
        fields = ["ingredient", "quantity", "expiration_date"]
        widgets = {
            "expiration_date": forms.DateInput(attrs={"type": "date"}),
        }

    def clean_quantity(self):
        quantity = self.cleaned_data.get("quantity")
        if quantity is not None and quantity <= 0:
            raise forms.ValidationError("Quantity must be greater than zero.")
        return quantity
