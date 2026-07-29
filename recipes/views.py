from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_GET, require_POST
from django.shortcuts import redirect

from pantry.models import PantryItem
from shopping_list.models import ShoppingListItem
from .forms import RecipeSearchFilterForm
from .models import Recipe, FavoriteRecipe


def get_pantry_quantities(user):
    """Returns a dictionary mapping ingredient_id -> quantity for a given user."""
    pantry_items = PantryItem.objects.filter(user=user)
    return {item.ingredient_id: item.quantity for item in pantry_items}


def _filter_recipes(request):
    """Helper function to validate filter GET params using RecipeSearchFilterForm."""
    form = RecipeSearchFilterForm(request.GET)
    recipes = Recipe.objects.all()

    if form.is_valid():
        search_query = form.cleaned_data.get('search_query')
        meal_type = form.cleaned_data.get('meal_type')
        category = form.cleaned_data.get('category')

        if search_query:
            recipes = recipes.filter(title__icontains=search_query)
        if meal_type:
            recipes = recipes.filter(meal_type=meal_type)
        if category:
            recipes = recipes.filter(category=category)

    return recipes.order_by('title'), form


@require_GET
def recipe_list(request):
    recipes, form = _filter_recipes(request)

    return render(
        request,
        'recipes/recipe_list.html',
        {
            'recipes': recipes[:20],
            'form': form,
        },
    )



@login_required
@require_GET
def recipe_detail(request, recipe_id):
    recipe = get_object_or_404(
        Recipe.objects.prefetch_related('recipeingredient_set__ingredient'),
        id=recipe_id,
    )

    pantry_quantities = get_pantry_quantities(request.user)

    shopping_quantities = {
        item.ingredient_id: item.quantity_needed
        for item in ShoppingListItem.objects.filter(user=request.user)
    }

    ingredients_with_status = []

    for ri in recipe.recipeingredient_set.all():
        available_qty = pantry_quantities.get(ri.ingredient.id, 0)
        has_enough = available_qty >= ri.required_quantity
        missing_qty = max(ri.required_quantity - available_qty, 0)
        shopping_qty = shopping_quantities.get(ri.ingredient.id, 0)
        # the shortfall is covered when the shopping list already holds
        # at least the amount the pantry is missing
        covers_shortfall = missing_qty > 0 and shopping_qty >= missing_qty

        ingredients_with_status.append({
            'ri': ri,
            'has_enough': has_enough,
            'available_qty': available_qty,
            'missing_qty': missing_qty,
            'shopping_qty': shopping_qty,
            'covers_shortfall': covers_shortfall,
        })

    all_missing_added = all(
        item['has_enough'] or item['covers_shortfall']
        for item in ingredients_with_status
    )

    is_favorite = FavoriteRecipe.objects.filter(user=request.user, recipe=recipe).exists()

    return render(
        request,
        'recipes/recipe_detail.html',
        {
            'recipe': recipe,
            'ingredients_with_status': ingredients_with_status,
            'all_missing_added': all_missing_added,
            'is_favorite': is_favorite,
        },
    )

@login_required
@require_GET
def recommended_recipes(request):
    pantry_ingredient_ids = set(
        PantryItem.objects.filter(user=request.user).values_list('ingredient_id', flat=True)
    )

    all_recipes = Recipe.objects.prefetch_related('recipeingredient_set__ingredient')
    scored_recipes = []

    for recipe in all_recipes:
        recipe_ingredients = recipe.recipeingredient_set.all()

        total_needed = len(recipe_ingredients)
        matched = sum(
            1
            for ri in recipe_ingredients
            if ri.ingredient.id in pantry_ingredient_ids
        )

        # rank by the percentage of ingredients we own, not the raw count,
        # so a short recipe you can fully cook beats a long one you can't
        match_percent = round(matched / total_needed * 100) if total_needed else 0

        scored_recipes.append({
            'recipe': recipe,
            'matched': matched,
            'total': total_needed,
            'match_percent': match_percent,
            'can_cook': total_needed > 0 and matched == total_needed,
        })

    scored_recipes.sort(key=lambda x: (x['match_percent'], x['matched']), reverse=True)

    return render(
        request,
        'recipes/recommended.html',
        {'scored_recipes': scored_recipes},
    )


@require_GET
def live_search(request):
    recipes, _ = _filter_recipes(request)

    return render(
        request,
        'recipes/_recipe_results.html',
        {'recipes': recipes[:20]},
    )


@login_required
def toggle_favorite(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)

    favorite = FavoriteRecipe.objects.filter(
        user=request.user,
        recipe=recipe,
    )

    if favorite.exists():
        favorite.delete()
    else:
        FavoriteRecipe.objects.create(
            user=request.user,
            recipe=recipe,
        )

    return redirect(
        "recipes:recipe_detail",
        recipe_id=recipe.id,
    )


@login_required
@require_GET
def favorite_recipes(request):
    favorites = (
        FavoriteRecipe.objects.filter(user=request.user)
        .select_related("recipe")
        .order_by("recipe__title")
    )

    return render(
        request,
        "recipes/favorites.html",
        {
            "favorites": favorites,
        },
    )


@login_required
@require_POST
def remove_favorite(request, recipe_id):
    FavoriteRecipe.objects.filter(
        user=request.user,
        recipe_id=recipe_id,
    ).delete()

    return redirect("recipes:favorite_recipes")


@login_required
@require_POST
def clear_favorites(request):
    FavoriteRecipe.objects.filter(
        user=request.user
    ).delete()

    return redirect("recipes:favorite_recipes")