from django import forms

from .models import PantryItem


class PantryItemForm(forms.ModelForm):
    class Meta:
        model = PantryItem
        fields = ["ingredient", "quantity", "expiration_date"]
        # the CSS classes are Bootstrap's, so the inputs match the rest of the site
        widgets = {
            "ingredient": forms.Select(
                attrs={"class": "form-select"}
            ),
            "quantity": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01", "min": "0.01"}
            ),
            "expiration_date": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
        }

    def clean_quantity(self):
        quantity = self.cleaned_data.get("quantity")
        if quantity is not None and quantity <= 0:
            raise forms.ValidationError("Quantity must be greater than zero.")
        return quantity
