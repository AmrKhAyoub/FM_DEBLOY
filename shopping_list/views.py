from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django.views.decorators.http import require_http_methods

from pantry.models import PantryItem
from recipes.models import Recipe
from .forms import ShoppingListItemForm, ShoppingListQuantityForm
from .models import ShoppingListItem




def _notify_item_saved(request, item, created):
    """Sends a standardized success message for added or updated items."""
    if created:
        messages.success(request, f'"{item.ingredient.title}" added to your shopping list!')
    else:
        messages.success(
            request,
            f'Updated "{item.ingredient.title}" — now {item.quantity_needed} {item.ingredient.unit}.',
        )


@login_required
def shopping_list(request):
    items = ShoppingListItem.objects.filter(user=request.user).select_related('ingredient')
    return render(request, 'shopping_list/shopping_list.html', {'items': items, 'form': ShoppingListItemForm()})


@login_required
@require_POST
def add_item(request):
    """
    Handles both ways of adding items to the shopping list.

    The same view is used for:
    1. Manual addition from the shopping list page.
    2. Adding ingredients from a recipe page

    Both use the same form, so the add/update logic only needs to be
    written once while still redirecting the user back to the page they
    came from.
    """
    form = ShoppingListItemForm(request.POST)

    if form.is_valid():
        # get the ingredient and quantity from the submitted form.
        ingredient = form.cleaned_data["ingredient"]
        quantity_needed = form.cleaned_data["quantity_needed"]

        # If the ingredient is already on the user's shopping list increase its quantity. Otherwise.. create a new item
        item, created = ShoppingListItem.objects.get_or_create(
            user=request.user,
            ingredient=ingredient,
            defaults={"quantity_needed": quantity_needed},
        )

        if not created:
            item.quantity_needed += quantity_needed
            item.full_clean()
            item.save()

        # Display a success message indicating whether the item was added or updated
        _notify_item_saved(request, item, created)

    else:
        messages.error(request, "Please fix the errors below.")

    # If the request came from a recipe page, return there.
    recipe_id = request.POST.get("recipe_id")
    if recipe_id:
        return redirect("recipes:recipe_detail", recipe_id=recipe_id)

    # otherwise, return to the shopping list page
    return redirect("shopping_list:shopping_list")


@login_required
def edit_item(request, item_id):
    item = get_object_or_404(ShoppingListItem, id=item_id, user=request.user)

    if request.method == 'POST':
        form = ShoppingListQuantityForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'quantity_needed': f'{item.quantity_needed:g}'})
            messages.success(request, f'Updated "{item.ingredient.title}".')
        elif request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)

    return redirect('shopping_list:shopping_list')


@login_required
@require_http_methods(["DELETE ,POST"])
def delete_item(request, item_id):
    item = get_object_or_404(ShoppingListItem, id=item_id, user=request.user)
    item.delete()
    messages.info(request, 'Item removed from your shopping list.')
    return redirect('shopping_list:shopping_list')



@login_required
def toggle_purchased(request, item_id):
    item = get_object_or_404(ShoppingListItem, id=item_id, user=request.user)
    item.is_purchased = not item.is_purchased
    item.save()

    if item.is_purchased:
        pantry_item, created = PantryItem.objects.get_or_create(
            user=request.user,
            ingredient=item.ingredient,
            defaults={'quantity': item.quantity_needed},
        )
        if not created:
            pantry_item.quantity += item.quantity_needed
            pantry_item.save()

    return redirect('shopping_list:shopping_list')


@login_required
@require_POST
def add_all_missing(request, recipe_id):
    recipe = get_object_or_404(
        Recipe.objects.prefetch_related('recipeingredient_set__ingredient'),
        id=recipe_id,
    )

    pantry = {item.ingredient_id: item.quantity for item in PantryItem.objects.filter(user=request.user)}
    existing_ids = set(ShoppingListItem.objects.filter(user=request.user).values_list('ingredient_id', flat=True))

    # Create a list of ShoppingListItem instances to be added in bulk
    items_to_create = [
        ShoppingListItem(
            user=request.user,
            ingredient=ri.ingredient,
            quantity_needed=ri.required_quantity - pantry.get(ri.ingredient_id, 0),
        )
        for ri in recipe.recipeingredient_set.all()
        if (ri.required_quantity - pantry.get(ri.ingredient_id, 0)) > 0
        and ri.ingredient_id not in existing_ids
    ]

    if items_to_create:
        ShoppingListItem.objects.bulk_create(items_to_create)
        messages.success(request, f'{len(items_to_create)} missing ingredient(s) added to your shopping list!')
    else:
        messages.info(request, "Nothing to add — you already have everything or it's all on your list.")

    return redirect('recipes:recipe_detail', recipe_id=recipe_id)