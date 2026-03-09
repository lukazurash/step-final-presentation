from django.shortcuts import render, get_object_or_404, redirect
from .models import Dish, Category, Cart, CartItem

def dish_list(request):
    dishes = Dish.objects.all()
    categories = Category.objects.all()

    
    category_id = request.GET.get('category')
    hotness = request.GET.get('hotness')
    is_nutty = request.GET.get('is_nutty')
    is_vegetarian = request.GET.get('is_vegetarian')

    if category_id and category_id != "all":
        dishes = dishes.filter(category_id=category_id)
    if hotness:
        dishes = dishes.filter(hotness=int(hotness))
    if is_nutty == 'yes':
        dishes = dishes.filter(is_nutty=True)
    if is_nutty == 'no':
        dishes = dishes.filter(is_nutty=False)
    if is_vegetarian == 'yes':
        dishes = dishes.filter(is_vegetarian=True)
    if is_vegetarian == 'no':
        dishes = dishes.filter(is_vegetarian=False)

    context = {
        'dishes': dishes,
        'categories': categories,
        'selected_category': category_id or 'all',
        'selected_hotness': hotness or '',
        'selected_nutty': is_nutty or '',
        'selected_vegetarian': is_vegetarian or '',
    }
    return render(request, 'menu/dish_list.html', context)


def get_cart(request):
    cart_id = request.session.get('cart_id')
    if cart_id:
        cart, created = Cart.objects.get_or_create(id=cart_id)
    else:
        cart = Cart.objects.create()
        request.session['cart_id'] = cart.id
    return cart

def add_to_cart(request, dish_id):
    cart = get_cart(request)
    dish = get_object_or_404(Dish, id=dish_id)
    item, created = CartItem.objects.get_or_create(cart=cart, dish=dish)
    if not created:
        item.quantity += 1
        item.save()
    return redirect('dish_list')

def remove_from_cart(request, item_id):
    cart = get_cart(request)
    item = get_object_or_404(CartItem, id=item_id, cart=cart)
    item.delete()
    return redirect('cart_view')

def update_cart(request, item_id):
    cart = get_cart(request)
    item = get_object_or_404(CartItem, id=item_id, cart=cart)
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        if quantity > 0:
            item.quantity = quantity
            item.save()
        else:
            item.delete()
    return redirect('cart_view')

def cart_view(request):
    cart = get_cart(request)
    items = CartItem.objects.filter(cart=cart)
    total_price = sum(item.dish.price * item.quantity for item in items)
    return render(request, 'menu/cart.html', {'cart_items': items, 'total_price': total_price})