from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods, require_POST

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


def _add_or_update_item(user, ingredient, quantity_needed):
    """
    Creates a shopping list item or increases its quantity if it already exists.
    """
    item, created = ShoppingListItem.objects.get_or_create(
        user=user,
        ingredient=ingredient,
        defaults={"quantity_needed": quantity_needed},
    )

    if not created:
        item.quantity_needed += quantity_needed
        item.full_clean()
        item.save()

    return item, created


@login_required
@require_http_methods(["GET"])
def shopping_list(request):
    items = ShoppingListItem.objects.filter(
        user=request.user
    ).select_related("ingredient")

    return render(
        request,
        "shopping_list/shopping_list.html",
        {
            "items": items,
            "form": ShoppingListItemForm(),
        },
    )


@login_required
@require_POST
def add_item(request):
    """
    Handles both ways of adding items to the shopping list.

    The same view is used for:
    1. Manual addition from the shopping list page.
    2. Adding ingredients from a recipe page.
    """
    form = ShoppingListItemForm(request.POST)

    if form.is_valid():
        ingredient = form.cleaned_data["ingredient"]
        quantity_needed = form.cleaned_data["quantity_needed"]

        item, created = _add_or_update_item(
            request.user,
            ingredient,
            quantity_needed,
        )

        _notify_item_saved(request, item, created)

    else:
        messages.error(request, "Please fix the errors below.")

    recipe_id = request.POST.get("recipe_id")
    if recipe_id:
        return redirect("recipes:recipe_detail", recipe_id=recipe_id)

    return redirect("shopping_list:shopping_list")


@login_required
@require_POST
def edit_item(request, item_id):
    item = get_object_or_404(
        ShoppingListItem,
        id=item_id,
        user=request.user,
    )

    form = ShoppingListQuantityForm(request.POST, instance=item)

    if form.is_valid():
        form.save()

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse(
                {
                    "success": True,
                    "quantity_needed": f"{item.quantity_needed:g}",
                }
            )

        messages.success(request, f'Updated "{item.ingredient.title}".')

    elif request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse(
            {
                "success": False,
                "errors": form.errors,
            },
            status=400,
        )

    return redirect("shopping_list:shopping_list")


@login_required
@require_http_methods(["DELETE", "POST"])
def delete_item(request, item_id):
    item = get_object_or_404(
        ShoppingListItem,
        id=item_id,
        user=request.user,
    )

    item.delete()
    messages.info(request, "Item removed from your shopping list.")

    return redirect("shopping_list:shopping_list")


@login_required
@require_POST
def clear_shopping_list(request):
    ShoppingListItem.objects.filter(
        user=request.user
    ).delete()

    return redirect("shopping_list:shopping_list")


@login_required
@require_POST
def toggle_purchased(request, item_id):
    item = get_object_or_404(
        ShoppingListItem,
        id=item_id,
        user=request.user,
    )

    item.is_purchased = not item.is_purchased
    item.save()

    if item.is_purchased:
        # buying an item moves its quantity into the pantry
        pantry_item, created = PantryItem.objects.get_or_create(
            user=request.user,
            ingredient=item.ingredient,
            defaults={"quantity": item.quantity_needed},
        )

        if not created:
            pantry_item.quantity += item.quantity_needed
            pantry_item.save()

        messages.success(
            request,
            f'"{item.ingredient.title}" moved to your pantry.',
        )
    else:
        # un-marking has to undo the transfer, otherwise toggling the same
        # item twice would add its quantity to the pantry again
        pantry_item = PantryItem.objects.filter(
            user=request.user,
            ingredient=item.ingredient,
        ).first()

        if pantry_item:
            remaining = pantry_item.quantity - item.quantity_needed

            if remaining > 0:
                pantry_item.quantity = remaining
                pantry_item.save()
            else:
                # nothing left of it, so drop the row instead of storing zero
                pantry_item.delete()

        messages.info(
            request,
            f'"{item.ingredient.title}" removed from your pantry again.',
        )

    return redirect("shopping_list:shopping_list")


@login_required
@require_POST
def add_all_missing(request, recipe_id):
    recipe = get_object_or_404(
        Recipe.objects.prefetch_related("recipeingredient_set__ingredient"),
        id=recipe_id,
    )

    pantry = {
        item.ingredient_id: item.quantity
        for item in PantryItem.objects.filter(user=request.user)
    }

    added_count = 0

    for ri in recipe.recipeingredient_set.all():
        missing_qty = ri.required_quantity - pantry.get(
            ri.ingredient_id,
            0,
        )

        if missing_qty > 0:
            _add_or_update_item(
                request.user,
                ri.ingredient,
                missing_qty,
            )
            added_count += 1

    if added_count:
        messages.success(
            request,
            f"{added_count} missing ingredient(s) added to your shopping list!",
        )
    else:
        messages.info(
            request,
            "Nothing to add — you already have everything or it's all on your list.",
        )

    return redirect(
        "recipes:recipe_detail",
        recipe_id=recipe_id,
    )