from django.db import models

class Recipe(models.Model):
    name = models.CharField(max_length=150)
    instructions = models.TextField()
    meal_type = models.CharField(max_length=50, blank=True)   # e.g. breakfast, lunch, dinner
    cuisine = models.CharField(max_length=50, blank=True)     # e.g. Italian, Sudanese

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='ingredients')
    ingredient_name = models.CharField(max_length=100)
    quantity = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"{self.ingredient_name} for {self.recipe.name}"