from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from recipes.models import Ingredient


class PantryItem(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="pantry_items"
    )
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        validators=[MinValueValidator(0.01, message="Quantity must be greater than zero.")]
    )
    expiration_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["expiration_date"]
        # Ensures uniqueness per batch (date) rather than just per ingredient
        constraints = [
            models.UniqueConstraint(
                fields=["user", "ingredient", "expiration_date"], 
                name="unique_user_ingredient_expiration"
            )
        ]

    def __str__(self):
        return f"{self.user.username}'s {self.ingredient.title} ({self.quantity} {self.ingredient.unit})"