from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from pantry.models import Ingredient


class Command(BaseCommand):
    help = 'Seeds the pantry with sample ingredients for the first user'

    def handle(self, *args, **kwargs):
        user = User.objects.first()

        if not user:
            self.stdout.write(self.style.ERROR('No users found. Create a superuser first.'))
            return

        # Clear this user's existing pantry items so we don't create duplicates
        Ingredient.objects.filter(owner=user).delete()

        sample_ingredients = [
            ('tomato', '3 pieces'),
            ('onion', '2 pieces'),
            ('garlic', '1 bulb'),
            ('egg', '6 pieces'),
            ('rice', '2 cups'),
            ('olive oil', '1 bottle'),
        ]

        for name, quantity in sample_ingredients:
            Ingredient.objects.create(owner=user, name=name, quantity=quantity)

        self.stdout.write(self.style.SUCCESS(f'Successfully seeded pantry for {user.username}!'))