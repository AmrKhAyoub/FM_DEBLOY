from django.core.management.base import BaseCommand
from recipes.models import Recipe, RecipeIngredient


class Command(BaseCommand):
    help = 'Seeds the database with sample recipes and ingredients'

    def handle(self, *args, **kwargs):
        # Clear existing recipes so we don't create duplicates if run twice
        Recipe.objects.all().delete()

        recipes_data = [
            {
                'name': 'Tomato Pasta',
                'instructions': 'Boil pasta until soft. In a pan, cook chopped tomato and garlic in oil for 5 minutes. Mix with pasta and serve.',
                'meal_type': 'dinner',
                'cuisine': 'Italian',
                'ingredients': [
                    ('pasta', '200g'),
                    ('tomato', '2 pieces'),
                    ('garlic', '2 cloves'),
                    ('olive oil', '2 tbsp'),
                ],
            },
            {
                'name': 'Vegetable Omelette',
                'instructions': 'Beat eggs with salt. Add chopped onion and pepper. Cook in a pan over medium heat until set.',
                'meal_type': 'breakfast',
                'cuisine': 'any',
                'ingredients': [
                    ('egg', '3 pieces'),
                    ('onion', '1 piece'),
                    ('pepper', '1 piece'),
                    ('salt', '1 pinch'),
                ],
            },
            {
                'name': 'Chicken Rice Bowl',
                'instructions': 'Cook rice. Grill chicken with spices. Serve chicken over rice with a side of vegetables.',
                'meal_type': 'lunch',
                'cuisine': 'Sudanese',
                'ingredients': [
                    ('chicken', '300g'),
                    ('rice', '1 cup'),
                    ('onion', '1 piece'),
                    ('spices', '1 tbsp'),
                ],
            },
            {
                'name': 'Lentil Soup',
                'instructions': 'Boil lentils with chopped onion and garlic until soft. Blend if desired. Season with salt and cumin.',
                'meal_type': 'lunch',
                'cuisine': 'Sudanese',
                'ingredients': [
                    ('lentils', '1 cup'),
                    ('onion', '1 piece'),
                    ('garlic', '2 cloves'),
                    ('cumin', '1 tsp'),
                ],
            },
            {
                'name': 'Greek Salad',
                'instructions': 'Chop tomato, cucumber, and onion. Mix with olive oil, salt, and a bit of lemon juice.',
                'meal_type': 'lunch',
                'cuisine': 'Greek',
                'ingredients': [
                    ('tomato', '2 pieces'),
                    ('cucumber', '1 piece'),
                    ('onion', '1 piece'),
                    ('olive oil', '2 tbsp'),
                ],
            },
        ]

        for data in recipes_data:
            recipe = Recipe.objects.create(
                name=data['name'],
                instructions=data['instructions'],
                meal_type=data['meal_type'],
                cuisine=data['cuisine'],
            )
            for ingredient_name, quantity in data['ingredients']:
                RecipeIngredient.objects.create(
                    recipe=recipe,
                    ingredient_name=ingredient_name,
                    quantity=quantity,
                )

        self.stdout.write(self.style.SUCCESS(f'Successfully seeded {len(recipes_data)} recipes!'))