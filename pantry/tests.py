from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from recipes.models import Ingredient

from .models import PantryItem

User = get_user_model()


class PantryViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="cook", password="pw-for-tests-123")
        self.client.force_login(self.user)
        self.milk = Ingredient.objects.create(title="Milk", unit="l")

    def test_page_loads(self):
        response = self.client.get(reverse("pantry:list"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pantry/pantry_list.html")

    def test_adding_the_same_ingredient_twice_sums_the_quantity(self):
        url = reverse("pantry:add")

        self.client.post(url, {"ingredient": self.milk.id, "quantity": "1.5"})
        self.client.post(url, {"ingredient": self.milk.id, "quantity": "2"})

        item = PantryItem.objects.get(user=self.user, ingredient=self.milk)
        self.assertEqual(item.quantity, Decimal("3.5"))

    def test_zero_quantity_is_rejected(self):
        self.client.post(
            reverse("pantry:add"), {"ingredient": self.milk.id, "quantity": "0"}
        )

        self.assertFalse(PantryItem.objects.filter(user=self.user).exists())

    def test_delete_confirmation_page_renders(self):
        """This page used to crash because its template did not exist."""
        item = PantryItem.objects.create(
            user=self.user, ingredient=self.milk, quantity=Decimal("2")
        )

        response = self.client.get(reverse("pantry:delete", args=[item.id]))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pantry/pantry_confirm_delete.html")
        self.assertContains(response, "Milk")

    def test_delete_removes_the_item(self):
        item = PantryItem.objects.create(
            user=self.user, ingredient=self.milk, quantity=Decimal("2")
        )

        self.client.post(reverse("pantry:delete", args=[item.id]))

        self.assertFalse(PantryItem.objects.filter(id=item.id).exists())

    def test_login_is_required(self):
        self.client.logout()

        response = self.client.get(reverse("pantry:list"))

        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)


class PantryOwnershipTests(TestCase):
    def test_cannot_delete_another_users_item(self):
        owner = User.objects.create_user(username="owner", password="pw-for-tests-123")
        intruder = User.objects.create_user(username="intruder", password="pw-for-tests-123")

        ingredient = Ingredient.objects.create(title="Butter", unit="g")
        item = PantryItem.objects.create(
            user=owner, ingredient=ingredient, quantity=Decimal("100")
        )

        self.client.force_login(intruder)
        response = self.client.post(reverse("pantry:delete", args=[item.id]))

        self.assertEqual(response.status_code, 404)
        self.assertTrue(PantryItem.objects.filter(id=item.id).exists())
