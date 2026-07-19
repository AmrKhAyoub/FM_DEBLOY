from django.shortcuts import render, get_object_or_404
from .models import Recipe
from pantry.models import Ingredient

def recipe_list(request):
    query = request.GET.get('q')
    meal_type = request.GET.get('meal_type')
    cuisine = request.GET.get('cuisine')

    recipes = Recipe.objects.all()

    if query:
        recipes = recipes.filter(name__icontains=query)

    if meal_type:
        recipes = recipes.filter(meal_type=meal_type)

    if cuisine:
        recipes = recipes.filter(cuisine__icontains=cuisine)

    return render(request, 'recipes/recipe_list.html', {
        'recipes': recipes,
        'query': query,
        'meal_type': meal_type,
        'cuisine': cuisine,
    })
def recipe_detail(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)

    pantry_items = Ingredient.objects.filter(owner=request.user)
    pantry_names = set(item.name.lower().strip() for item in pantry_items)

    ingredients_with_status = []
    for ri in recipe.ingredients.all():
        has_it = ri.ingredient_name.lower().strip() in pantry_names
        ingredients_with_status.append({
            'ingredient': ri,
            'has_it': has_it,
        })

    return render(request, 'recipes/recipe_detail.html', {
        'recipe': recipe,
        'ingredients_with_status': ingredients_with_status,
    })


def recommended_recipes(request):
    # Get all ingredient names the user has, lowercased for comparison
    pantry_items = Ingredient.objects.filter(owner=request.user)
    pantry_names = set(item.name.lower().strip() for item in pantry_items)

    all_recipes = Recipe.objects.all()
    scored_recipes = []

    for recipe in all_recipes:
        recipe_ingredients = recipe.ingredients.all()
        total_needed = recipe_ingredients.count()
        matched = 0

        for ri in recipe_ingredients:
            if ri.ingredient_name.lower().strip() in pantry_names:
                matched += 1

        scored_recipes.append({
            'recipe': recipe,
            'matched': matched,
            'total': total_needed,
        })

    # Sort by matched count, highest first
    scored_recipes.sort(key=lambda x: x['matched'], reverse=True)

    return render(request, 'recipes/recommended.html', {'scored_recipes': scored_recipes})
    