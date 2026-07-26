from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render

from pantry.models import PantryItem
from shopping_list.models import ShoppingListItem
from .models import Recipe


def get_pantry_quantities(user):
    """Returns a dictionary mapping ingredient_id -> quantity for a given user."""
    pantry_items = PantryItem.objects.filter(user=user)
    return {item.ingredient_id: item.quantity for item in pantry_items}


def _filter_recipes(request):
    """Helper function to filter recipes based on query parameters."""
    query = request.GET.get('q')
    meal_type = request.GET.get('meal_type')
    category = request.GET.get('category')

    recipes = Recipe.objects.all()

    if query:
        recipes = recipes.filter(title__icontains=query)
    if meal_type:
        recipes = recipes.filter(meal_type=meal_type)
    if category:
        recipes = recipes.filter(category=category)

    # Fixed unordered slicing by adding explicit order_by
    return recipes.order_by('title'), query, meal_type, category


def recipe_list(request):
    recipes, query, meal_type, category = _filter_recipes(request)

    return render(
        request,
        'recipes/recipe_list.html',
        {
            'recipes': recipes[:20],
            'query': query,
            'meal_type': meal_type,
            'category': category,
        },
    )


@login_required
def recipe_detail(request, recipe_id):
    recipe = get_object_or_404(
        Recipe.objects.prefetch_related('recipeingredient_set__ingredient'),
        id=recipe_id,
    )

    pantry_quantities = get_pantry_quantities(request.user)

    shopping_ingredient_ids = set(
        ShoppingListItem.objects.filter(user=request.user).values_list('ingredient_id', flat=True)
    )

    ingredients_with_status = []
    for ri in recipe.recipeingredient_set.all():
        available_qty = pantry_quantities.get(ri.ingredient.id, 0)
        has_enough = available_qty >= ri.required_quantity
        missing_qty = max(ri.required_quantity - available_qty, 0)
        in_shopping_list = ri.ingredient.id in shopping_ingredient_ids

        ingredients_with_status.append({
            'ri': ri,
            'has_enough': has_enough,
            'available_qty': available_qty,
            'missing_qty': missing_qty,
            'in_shopping_list': in_shopping_list,
        })

    all_missing_added = all(
        item['has_enough'] or item['in_shopping_list']
        for item in ingredients_with_status
    )

    return render(
        request,
        'recipes/recipe_detail.html',
        {
            'recipe': recipe,
            'ingredients_with_status': ingredients_with_status,
            'all_missing_added': all_missing_added,
        },
    )


@login_required
def recommended_recipes(request):
    pantry_ingredient_ids = set(
        PantryItem.objects.filter(user=request.user).values_list('ingredient_id', flat=True)
    )

    all_recipes = Recipe.objects.prefetch_related('recipeingredient_set__ingredient')
    scored_recipes = []

    for recipe in all_recipes:
        recipe_ingredients = recipe.recipeingredient_set.all()
        
        total_needed = len(recipe_ingredients)
        matched = sum(1 for ri in recipe_ingredients if ri.ingredient.id in pantry_ingredient_ids)

        scored_recipes.append({
            'recipe': recipe,
            'matched': matched,
            'total': total_needed,
        })

    scored_recipes.sort(key=lambda x: x['matched'], reverse=True)

    return render(request, 'recipes/recommended.html', {'scored_recipes': scored_recipes})


def live_search(request):
    recipes, _, _, _ = _filter_recipes(request)

    return render(request, 'recipes/_recipe_results.html', {'recipes': recipes[:20]})