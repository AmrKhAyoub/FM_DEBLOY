from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import ShoppingListItem


@login_required #restricting personal data views to logged-in users only
def shopping_list(request):
    items = ShoppingListItem.objects.filter(owner=request.user)
    return render(request, 'shopping_list/shopping_list.html', {'items': items})


@login_required
def add_item(request):
    if request.method == 'POST':
        item_name = request.POST.get('item_name')
        quantity = request.POST.get('quantity')

        if item_name:
            ShoppingListItem.objects.create(
                owner=request.user,
                item_name=item_name,
                quantity=quantity,
            )
            messages.success(request, f'"{item_name}" added to your shopping list!')

    return redirect('shopping_list')

from django.http import JsonResponse

@login_required
def edit_item(request, item_id):
    item = get_object_or_404(ShoppingListItem, id=item_id, owner=request.user)
    if request.method == 'POST':
        item.quantity = request.POST.get('quantity')
        item.save()

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'quantity': item.quantity})

        messages.success(request, f'Updated "{item.item_name}".')

    return redirect('shopping_list')

@login_required
def delete_item(request, item_id):
    item = get_object_or_404(ShoppingListItem, id=item_id, owner=request.user)
    item.delete()
    return redirect('shopping_list')


@login_required
def toggle_purchased(request, item_id):
    item = get_object_or_404(ShoppingListItem, id=item_id, owner=request.user)
    item.purchased = not item.purchased
    item.save()
    return redirect('shopping_list')

from django.contrib import messages

@login_required
def add_from_recipe(request):
    if request.method == 'POST':
        item_name = request.POST.get('item_name')
        quantity = request.POST.get('quantity', '')

        already_exists = ShoppingListItem.objects.filter(
            owner=request.user,
            item_name__iexact=item_name
        ).exists()

        if item_name and not already_exists:
            ShoppingListItem.objects.create(
                owner=request.user,
                item_name=item_name,
                quantity=quantity,
            )

    recipe_id = request.POST.get('recipe_id')
    return redirect('recipe_detail', recipe_id=recipe_id)


