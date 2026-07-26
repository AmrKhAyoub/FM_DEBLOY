from django import forms
from .models import Recipe


class RecipeSearchFilterForm(forms.Form):
    search_query = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Search recipes by name...",
            }
        ),
    )

    meal_type = forms.ChoiceField(
        choices=[("", "All Meal Types")] + Recipe.MealTypeChoices.choices,
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    category = forms.ChoiceField(
        choices=[("", "All Categories")] + Recipe.RecipeCategoryChoices.choices,
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
    )