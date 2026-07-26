from django import forms
from django.core.exceptions import ValidationError
from .models import ShoppingListItem


class ShoppingListItemForm(forms.ModelForm):
    class Meta:
        model = ShoppingListItem
        fields = ['ingredient', 'quantity_needed']
        widgets = {
            'ingredient': forms.Select(attrs={'class': 'form-select'}),
            'quantity_needed': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'}),
        }


class ShoppingListQuantityForm(forms.ModelForm):
    class Meta:
        model = ShoppingListItem
        fields = ['quantity_needed']
        widgets = {
            'quantity_needed': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'}),
        }