from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from pantry.models import PantryItem
from recipes.models import Ingredient, Recipe, RecipeIngredient

from .models import ShoppingListItem

User = get_user_model()


class TogglePurchasedTests(TestCase):
    """Buying an item moves it to the pantry, and undoing it takes it back."""

    def setUp(self):
        self.user = User.objects.create_user(username="cook", password="pw-for-tests-123")
        self.client.force_login(self.user)

        self.flour = Ingredient.objects.create(title="Flour", unit="g")
        self.item = ShoppingListItem.objects.create(
            user=self.user, ingredient=self.flour, quantity_needed=Decimal("500")
        )
        self.url = reverse("shopping_list:toggle_purchased", args=[self.item.id])

    def test_buying_adds_the_quantity_to_the_pantry(self):
        self.client.post(self.url)

        pantry_item = PantryItem.objects.get(user=self.user, ingredient=self.flour)
        self.assertEqual(pantry_item.quantity, Decimal("500"))

    def test_buying_adds_on_top_of_what_is_already_there(self):
        PantryItem.objects.create(
            user=self.user, ingredient=self.flour, quantity=Decimal("200")
        )

        self.client.post(self.url)

        pantry_item = PantryItem.objects.get(user=self.user, ingredient=self.flour)
        self.assertEqual(pantry_item.quantity, Decimal("700"))

    def test_toggling_twice_does_not_double_count(self):
        """Regression test: un-marking used to leave the quantity in the pantry,
        so buying the same item again added it a second time."""
        self.client.post(self.url)  # bought
        self.client.post(self.url)  # undo
        self.client.post(self.url)  # bought again

        pantry_item = PantryItem.objects.get(user=self.user, ingredient=self.flour)
        self.assertEqual(pantry_item.quantity, Decimal("500"))

    def test_undo_removes_the_row_when_nothing_is_left(self):
        self.client.post(self.url)  # bought
        self.client.post(self.url)  # undo

        self.assertFalse(
            PantryItem.objects.filter(user=self.user, ingredient=self.flour).exists()
        )

    def test_undo_keeps_the_quantity_that_was_there_before(self):
        PantryItem.objects.create(
            user=self.user, ingredient=self.flour, quantity=Decimal("200")
        )

        self.client.post(self.url)  # bought -> 700
        self.client.post(self.url)  # undo -> back to 200

        pantry_item = PantryItem.objects.get(user=self.user, ingredient=self.flour)
        self.assertEqual(pantry_item.quantity, Decimal("200"))


class AddItemTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="cook", password="pw-for-tests-123")
        self.client.force_login(self.user)
        self.rice = Ingredient.objects.create(title="Rice", unit="g")

    def test_adding_the_same_ingredient_twice_sums_the_quantity(self):
        url = reverse("shopping_list:add_item")

        self.client.post(url, {"ingredient": self.rice.id, "quantity_needed": "100"})
        self.client.post(url, {"ingredient": self.rice.id, "quantity_needed": "150"})

        item = ShoppingListItem.objects.get(user=self.user, ingredient=self.rice)
        self.assertEqual(item.quantity_needed, Decimal("250"))

    def test_zero_quantity_is_rejected(self):
        self.client.post(
            reverse("shopping_list:add_item"),
            {"ingredient": self.rice.id, "quantity_needed": "0"},
        )

        self.assertFalse(ShoppingListItem.objects.filter(user=self.user).exists())


class AddAllMissingTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="cook", password="pw-for-tests-123")
        self.client.force_login(self.user)

        self.recipe = Recipe.objects.create(title="Bread")
        self.flour = Ingredient.objects.create(title="Flour", unit="g")
        self.salt = Ingredient.objects.create(title="Salt", unit="g")

        RecipeIngredient.objects.create(
            recipe=self.recipe, ingredient=self.flour, required_quantity=Decimal("500")
        )
        RecipeIngredient.objects.create(
            recipe=self.recipe, ingredient=self.salt, required_quantity=Decimal("10")
        )

    def test_only_the_shortfall_is_added(self):
        # we already have all the salt and part of the flour
        PantryItem.objects.create(
            user=self.user, ingredient=self.salt, quantity=Decimal("50")
        )
        PantryItem.objects.create(
            user=self.user, ingredient=self.flour, quantity=Decimal("200")
        )

        self.client.post(
            reverse("shopping_list:add_all_missing", args=[self.recipe.id])
        )

        items = ShoppingListItem.objects.filter(user=self.user)
        self.assertEqual(items.count(), 1)
        self.assertEqual(items.first().ingredient, self.flour)
        self.assertEqual(items.first().quantity_needed, Decimal("300"))

    def test_nothing_is_added_when_the_pantry_covers_everything(self):
        PantryItem.objects.create(
            user=self.user, ingredient=self.salt, quantity=Decimal("50")
        )
        PantryItem.objects.create(
            user=self.user, ingredient=self.flour, quantity=Decimal("900")
        )

        self.client.post(
            reverse("shopping_list:add_all_missing", args=[self.recipe.id])
        )

        self.assertFalse(ShoppingListItem.objects.filter(user=self.user).exists())


class OwnershipTests(TestCase):
    """A user must never be able to touch another user's rows."""

    def test_cannot_delete_another_users_item(self):
        owner = User.objects.create_user(username="owner", password="pw-for-tests-123")
        intruder = User.objects.create_user(username="intruder", password="pw-for-tests-123")

        ingredient = Ingredient.objects.create(title="Sugar", unit="g")
        item = ShoppingListItem.objects.create(
            user=owner, ingredient=ingredient, quantity_needed=Decimal("100")
        )

        self.client.force_login(intruder)
        response = self.client.post(
            reverse("shopping_list:delete_item", args=[item.id])
        )

        self.assertEqual(response.status_code, 404)
        self.assertTrue(ShoppingListItem.objects.filter(id=item.id).exists())
