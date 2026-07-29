import json
from pathlib import Path

from django.core.management.base import BaseCommand
from recipes.models import Ingredient, Recipe, RecipeIngredient


class Command(BaseCommand):
    help = "Seed recipes from recipe_data.json"

    def handle(self, *args, **kwargs):

        json_path = (
          Path(__file__).resolve().parents[3]
          / "data_recipes.json"
        )

        with open(json_path, "r", encoding="utf-8") as file:
            recipes = json.load(file)

        # Clear old data
        RecipeIngredient.objects.all().delete()
        Recipe.objects.all().delete()

        created = 0

        for recipe_data in recipes:

            recipe = Recipe.objects.create(
                title=recipe_data["title"],
                instructions=recipe_data["instructions"],
                prep_time=recipe_data["prep_time"],
                meal_type=recipe_data["meal_type"],
                category=recipe_data["category"],
                image_url=recipe_data.get("image_url", ""),
            )

            for ingredient_data in recipe_data["ingredients"]:

                ingredient, _ = Ingredient.objects.get_or_create(
                    title=ingredient_data["title"],
                    defaults={
                        "category": ingredient_data["category"],
                        "unit": ingredient_data["unit"],
                    },
                )

                RecipeIngredient.objects.create(
                    recipe=recipe,
                    ingredient=ingredient,
                    required_quantity=ingredient_data["required_quantity"],
                )

            created += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully imported {created} recipes."
            )
        )