from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from recipes.models import Ingredient


class PantryItem(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="pantry_items"
    )
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    # add  minValuevlider to prevent negative or zero quantities in the database
    quantity = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        validators=[MinValueValidator(0.01, message="Quantity must be greater than zero.")]
    )
    expiration_date = models.DateField(null=True, blank=True)

    class Meta:
        # add unique constraint to ensure that a user cannot have duplicate ingredients in their pantry
        constraints = [
            models.UniqueConstraint(fields=["user", "ingredient"], name="unique_user_pantry_ingredient")
        ]

    def __str__(self):
        return f"{self.user.username}'s {self.ingredient.title} ({self.quantity} {self.ingredient.unit})"