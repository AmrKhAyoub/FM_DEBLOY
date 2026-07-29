from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class RegistrationTests(TestCase):
    def test_register_creates_a_user(self):
        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "newcook",
                "email": "newcook@example.com",
                "password1": "a-strong-pw-2026",
                "password2": "a-strong-pw-2026",
            },
        )

        self.assertRedirects(response, reverse("accounts:login"))
        self.assertTrue(User.objects.filter(username="newcook").exists())

    def test_mismatched_passwords_are_rejected(self):
        self.client.post(
            reverse("accounts:register"),
            {
                "username": "newcook",
                "email": "newcook@example.com",
                "password1": "a-strong-pw-2026",
                "password2": "a-different-pw-2026",
            },
        )

        self.assertFalse(User.objects.filter(username="newcook").exists())


class ProfileTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="cook", email="cook@example.com", password="pw-for-tests-123"
        )

    def test_profile_requires_login(self):
        response = self.client.get(reverse("accounts:profile"))

        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    def test_profile_shows_the_logged_in_user(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("accounts:profile"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "cook@example.com")

    def test_editing_the_profile(self):
        self.client.force_login(self.user)

        self.client.post(
            reverse("accounts:edit_profile"),
            {"username": "cook", "email": "updated@example.com"},
        )

        self.user.refresh_from_db()
        self.assertEqual(self.user.email, "updated@example.com")

    def test_deleting_the_account(self):
        self.client.force_login(self.user)

        self.client.post(reverse("accounts:delete_account"))

        self.assertFalse(User.objects.filter(username="cook").exists())


class PageRenderTests(TestCase):
    """Every page returns 200 and uses the shared base layout."""

    def setUp(self):
        self.user = User.objects.create_user(username="cook", password="pw-for-tests-123")
        self.client.force_login(self.user)

    def test_all_main_pages_render(self):
        pages = [
            reverse("recipes:recipe_list"),
            reverse("recipes:recommended_recipes"),
            reverse("recipes:favorite_recipes"),
            reverse("pantry:list"),
            reverse("shopping_list:shopping_list"),
            reverse("accounts:profile"),
            reverse("accounts:edit_profile"),
            reverse("accounts:change_password"),
            reverse("accounts:delete_account"),
        ]

        for url in pages:
            with self.subTest(url=url):
                response = self.client.get(url)

                self.assertEqual(response.status_code, 200)
                # the navbar only exists in base.html, so finding it proves
                # the page really extends the shared layout
                self.assertContains(response, "Smart Meal Planner")
                self.assertContains(response, "custom-navbar")
