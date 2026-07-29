from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from pantry.models import PantryItem
from shopping_list.models import ShoppingListItem

from .models import FavoriteRecipe, Ingredient, Recipe, RecipeIngredient

User = get_user_model()


class RecipeSearchTests(TestCase):
    """The search box sends the field names of RecipeSearchFilterForm."""

    def setUp(self):
        Recipe.objects.create(title="Lentil Soup", meal_type="lunch", category="soups")
        Recipe.objects.create(title="Chocolate Cake", meal_type="snack", category="dessert")

    def test_search_query_filters_by_title(self):
        response = self.client.get(reverse("recipes:recipe_list"), {"search_query": "lentil"})

        self.assertContains(response, "Lentil Soup")
        self.assertNotContains(response, "Chocolate Cake")

    def test_meal_type_filter(self):
        response = self.client.get(reverse("recipes:recipe_list"), {"meal_type": "snack"})

        self.assertContains(response, "Chocolate Cake")
        self.assertNotContains(response, "Lentil Soup")

    def test_category_filter(self):
        response = self.client.get(reverse("recipes:recipe_list"), {"category": "soups"})

        self.assertContains(response, "Lentil Soup")
        self.assertNotContains(response, "Chocolate Cake")

    def test_live_search_returns_only_the_results_partial(self):
        response = self.client.get(reverse("recipes:live_search"), {"search_query": "cake"})

        self.assertContains(response, "Chocolate Cake")
        # the partial must not carry the whole page layout with it
        self.assertNotContains(response, "<nav")


class RecipeDetailStatusTests(TestCase):
    """Each ingredient is compared against the pantry and the shopping list."""

    def setUp(self):
        self.user = User.objects.create_user(username="cook", password="pw-for-tests-123")
        self.client.force_login(self.user)

        self.recipe = Recipe.objects.create(title="Omelette")
        self.eggs = Ingredient.objects.create(title="Eggs", unit="pcs")
        RecipeIngredient.objects.create(
            recipe=self.recipe, ingredient=self.eggs, required_quantity=4
        )

    def _status(self):
        response = self.client.get(
            reverse("recipes:recipe_detail", args=[self.recipe.id])
        )
        return response, response.context["ingredients_with_status"][0]

    def test_enough_in_pantry(self):
        PantryItem.objects.create(user=self.user, ingredient=self.eggs, quantity=6)

        response, status = self._status()

        self.assertTrue(status["has_enough"])
        self.assertEqual(status["missing_qty"], 0)
        self.assertTrue(response.context["all_missing_added"])

    def test_missing_when_pantry_is_short(self):
        PantryItem.objects.create(user=self.user, ingredient=self.eggs, quantity=1)

        response, status = self._status()

        self.assertFalse(status["has_enough"])
        self.assertEqual(status["missing_qty"], 3)
        self.assertFalse(status["covers_shortfall"])
        self.assertFalse(response.context["all_missing_added"])

    def test_shortfall_is_covered_by_the_shopping_list(self):
        PantryItem.objects.create(user=self.user, ingredient=self.eggs, quantity=1)
        ShoppingListItem.objects.create(
            user=self.user, ingredient=self.eggs, quantity_needed=3
        )

        response, status = self._status()

        self.assertTrue(status["covers_shortfall"])
        self.assertTrue(response.context["all_missing_added"])


class RecommendationTests(TestCase):
    """Recipes are ranked by the percentage of ingredients owned, not the count."""

    def setUp(self):
        self.user = User.objects.create_user(username="cook", password="pw-for-tests-123")
        self.client.force_login(self.user)

        self.owned = [
            Ingredient.objects.create(title=f"Owned {i}", unit="g") for i in range(4)
        ]
        self.missing = [
            Ingredient.objects.create(title=f"Missing {i}", unit="g") for i in range(6)
        ]
        for ingredient in self.owned:
            PantryItem.objects.create(user=self.user, ingredient=ingredient, quantity=100)

        # 2 of 2 ingredients owned -> 100%
        self.short = Recipe.objects.create(title="Short Recipe")
        for ingredient in self.owned[:2]:
            RecipeIngredient.objects.create(
                recipe=self.short, ingredient=ingredient, required_quantity=1
            )

        # 4 of 10 ingredients owned -> 40%, but a higher raw count
        self.long = Recipe.objects.create(title="Long Recipe")
        for ingredient in self.owned + self.missing:
            RecipeIngredient.objects.create(
                recipe=self.long, ingredient=ingredient, required_quantity=1
            )

    def test_fully_cookable_recipe_ranks_first(self):
        response = self.client.get(reverse("recipes:recommended_recipes"))
        scored = response.context["scored_recipes"]

        self.assertEqual(scored[0]["recipe"], self.short)
        self.assertEqual(scored[0]["match_percent"], 100)
        self.assertTrue(scored[0]["can_cook"])

        self.assertEqual(scored[1]["match_percent"], 40)
        self.assertFalse(scored[1]["can_cook"])

    def test_recipe_without_ingredients_does_not_crash(self):
        Recipe.objects.create(title="Empty Recipe")

        response = self.client.get(reverse("recipes:recommended_recipes"))

        self.assertEqual(response.status_code, 200)


class FavoriteTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="cook", password="pw-for-tests-123")
        self.client.force_login(self.user)
        self.recipe = Recipe.objects.create(title="Pancakes")

    def test_toggle_adds_then_removes(self):
        url = reverse("recipes:toggle_favorite", args=[self.recipe.id])

        self.client.post(url)
        self.assertTrue(FavoriteRecipe.objects.filter(user=self.user).exists())

        self.client.post(url)
        self.assertFalse(FavoriteRecipe.objects.filter(user=self.user).exists())

    def test_detail_requires_login(self):
        self.client.logout()

        response = self.client.get(
            reverse("recipes:recipe_detail", args=[self.recipe.id])
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)
