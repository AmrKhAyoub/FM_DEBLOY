from django.db import models
from django.conf import settings


class Ingredient(models.Model):
    class CategoryChoices(models.TextChoices):
        VEGETABLES = "vegetables", "Vegetables"
        FRUITS = "fruits", "Fruits"
        MEAT = "meat", "Meat"
        DAIRY = "dairy", "Dairy"
        SPICES = "spices", "Spices"
        GRAINS = "grains", "Grains"
        OTHER = "other", "Other"

    class QuantityUnitChoices(models.TextChoices):
        GRAM = "g", "Grams"
        KILOGRAM = "kg", "Kilograms"
        MILLILITER = "ml", "Milliliters"
        LITER = "l", "Liters"
        TEASPOON = "tsp", "Teaspoon"
        PIECE = "pcs", "Pieces"
        OTHER = "other", "Other"

    title = models.CharField(max_length=100, unique=True)
    category = models.CharField(
        max_length=50,
        choices=CategoryChoices.choices,
        default=CategoryChoices.OTHER,
    )
    unit = models.CharField(
        max_length=50,
        choices=QuantityUnitChoices.choices,
        default=QuantityUnitChoices.OTHER,
    )

    def __str__(self):
        return self.title


class Recipe(models.Model):
    class MealTypeChoices(models.TextChoices):
        BREAKFAST = "breakfast", "Breakfast"
        LUNCH = "lunch", "Lunch"
        DINNER = "dinner", "Dinner"
        SNACK = "snack", "Snack"

    class RecipeCategoryChoices(models.TextChoices):
        DESSERT = "dessert", "Dessert"
        PASTRIES = "pastries", "Pastries"
        GRILLS = "grills", "Grills"
        SOUPS = "soups", "Soups"
        SALADS = "salads", "Salads"
        MAIN_DISH = "main_dish", "Main Dish"

    title = models.CharField(max_length=200, unique=True)
    # fixed typo in help text 'prepration' -> 'preparation'
    instructions = models.TextField(
        help_text="instructions of preparation", null=True, blank=True
    )
    prep_time = models.PositiveIntegerField(null=True, blank=True)

    meal_type = models.CharField(
        max_length=50,
        choices=MealTypeChoices.choices,
        null=True,
        blank=True,
    )

    category = models.CharField(
        max_length=50,
        choices=RecipeCategoryChoices.choices,
        null=True,
        blank=True,
    )

    image_url = models.URLField(blank=True)

    ingredients = models.ManyToManyField(Ingredient, through="RecipeIngredient")

    # emoji shown on the recipe cards, one per category. It is a property and
    # not a database column, so no migration is needed to change it.
    CATEGORY_ICONS = {
        RecipeCategoryChoices.DESSERT: "🍰",
        RecipeCategoryChoices.PASTRIES: "🥐",
        RecipeCategoryChoices.GRILLS: "🍖",
        RecipeCategoryChoices.SOUPS: "🍲",
        RecipeCategoryChoices.SALADS: "🥗",
        RecipeCategoryChoices.MAIN_DISH: "🍽️",
    }

    @property
    def icon(self):
        return self.CATEGORY_ICONS.get(self.category, "🍳")

    def __str__(self):
        return self.title


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    required_quantity = models.DecimalField(max_digits=8, decimal_places=2)

    class Meta:
        # make the combination of recipe and ingredient unique to prevent duplicates
        constraints = [
            models.UniqueConstraint(fields=["recipe", "ingredient"], name="unique_recipe_ingredient")
        ]

    def __str__(self):
        return f"{self.required_quantity} {self.ingredient.unit} of {self.ingredient.title} for {self.recipe.title}"


# favorite Recipe Model
class FavoriteRecipe(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"],
                name="unique_user_favorite_recipe",
            )
        ]

    def __str__(self):
        return f"{self.user} - {self.recipe}"