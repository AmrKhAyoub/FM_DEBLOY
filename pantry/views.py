from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from .forms import PantryItemForm
from .models import PantryItem


@login_required
@require_http_methods(["GET"])
def pantry_list_view(request):
    pantry_items = PantryItem.objects.select_related("ingredient").filter(
        user=request.user
    )
    context = {"pantry_items": pantry_items}
    return render(request, "pantry/pantry_list.html", context)


@login_required
@require_http_methods(["GET", "POST"])
def pantry_add_view(request):
    if request.method == "GET":
        form = PantryItemForm()
        return render(request, "pantry/pantry_form.html", {"form": form})

    form = PantryItemForm(request.POST)

    if not form.is_valid():
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse(form.errors, status=400)

        return render(
            request,
            "pantry/pantry_form.html",
            {"form": form},
        )

    ingredient = form.cleaned_data["ingredient"]
    quantity = form.cleaned_data["quantity"]
    expiration_date = form.cleaned_data.get("expiration_date")

    existing_item = PantryItem.objects.filter(
        user=request.user, ingredient=ingredient
    ).first()

    if existing_item:
        existing_item.quantity += quantity
        fields_to_update = ["quantity"]

        if expiration_date:
            existing_item.expiration_date = expiration_date
            fields_to_update.append("expiration_date")

        # use update_fields to avoid overwriting unnecessary fields
        existing_item.save(update_fields=fields_to_update)
        item = existing_item
        message = "Ingredient already exists. Quantity updated successfully!"
    else:
        item = form.save(commit=False)
        item.user = request.user
        item.save()
        message = "Item saved successfully."

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        data = {
            "id": item.id,
            "ingredient_name": item.ingredient.title,
            "quantity": item.quantity,
            "unit": item.ingredient.unit,
            "message": message,
        }
        return JsonResponse(data, status=200)

    return redirect("pantry:list")


@login_required
@require_http_methods(["GET", "POST"])
def pantry_update_view(request, pk):
    item = get_object_or_404(PantryItem, pk=pk, user=request.user)

    if request.method == "GET":
        form = PantryItemForm(instance=item)
        return render(request, "pantry/pantry_form.html", {"form": form, "item": item})

    form = PantryItemForm(request.POST, instance=item)

    if not form.is_valid():
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse(form.errors, status=400)

        return render(request, "pantry/pantry_form.html", {"form": form, "item": item})

    item = form.save()
    message = "Item updated successfully."

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        data = {
            "id": item.id,
            "ingredient_name": item.ingredient.title,
            "quantity": item.quantity,
            "unit": item.ingredient.unit,
            "message": message,
        }
        return JsonResponse(data, status=200)

    return redirect("pantry:list")


@login_required
#add @require_http_methods to restrict the view to GET and POST requests
@require_http_methods(["GET", "POST"])
def pantry_delete_view(request, pk):
    item = get_object_or_404(PantryItem, pk=pk, user=request.user)

    if request.method == "GET":
        return render(request, "pantry/pantry_confirm_delete.html", {"object": item})

    item.delete()
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({"message": "Item deleted successfully."}, status=200)
    return redirect("pantry:list")