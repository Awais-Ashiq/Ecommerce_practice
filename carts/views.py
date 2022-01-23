from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from store.models import Product, Variation
from .models import CartItem, Cart

# Create your views here.

def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

def add_cart(request, product_id):
    product = Product.objects.get(pk=product_id)
    product_variations = []
    if request.method == 'POST':
        for key in request.POST:
            value = request.POST[key]
            try:
                variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
                product_variations.append(variation)
            except:
                pass
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(cart_id = _cart_id(request))
        cart.save()
    is_cart_item = CartItem.objects.filter(product=product, cart=cart).exists()
    if is_cart_item:
        cart_item = CartItem.objects.filter(product=product, cart=cart)
        ex_var_list = []
        id = []
        for item in cart_item:
            ex_var_list.append(list(item.variation.all()))
            id.append(item.id)
        print(ex_var_list)    
        if product_variations in ex_var_list:
            index = ex_var_list.index(product_variations)
            item_id = id[index]
            item = CartItem.objects.get(product=product, id=item_id)
            item.quantity += 1
            item.save()
        else:
            item = CartItem.objects.create(product=product, cart=cart, quantity=1)
            if product_variations:
                item.variation.clear()
                item.variation.add(*product_variations)
        
            item.save()
    else:
        cart_item = CartItem.objects.create(
            product=product,
            quantity=1,
            cart=cart,
        )
        if product_variations:
            cart_item.variation.clear()
            cart_item.variation.add(*product_variations)
        cart_item.save()
    return redirect('cart')

def remove_cart(request, product_id, cart_id):
    product = Product.objects.get(pk=product_id)
    cart = Cart.objects.get(cart_id=_cart_id(request))
    cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_id)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
    else:
        cart_item.delete()
    cart_item.save()
    return redirect('cart')

def remove_cart_item(request, product_id, cart_id):
    try:
        product = get_object_or_404(Product, pk=product_id)
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_id)
        cart_item.delete()
    except Exception as e:
        # return HttpResponse("No Object:"+ str(e))
        pass
    return redirect('cart')


def cart(request, total=0, quantity=0, cart_items=None):
    cart_items_count=0
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        cart_items_count = 0
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity = cart_item.quantity
            cart_items_count += quantity
    except Cart.DoesNotExist:
        pass
    context = {
        'total':total,
        'quantity':quantity,
        'cart_items': cart_items,
        'cart_items_count':cart_items_count,
    }
    return render(request, 'store/cart.html', context)