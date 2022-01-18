from tkinter import E
from unicodedata import category
from django.shortcuts import render
from carts.models import CartItem
from store.models import Product
from category.models import Category
from carts.views import _cart_id

def store(request, category_slug=None):
    products=None
    if category_slug:
        products = Product.objects.filter(category__slug=category_slug).filter(is_available=True)
        products_count = products.count()
    else:
        products = Product.objects.all().filter(is_available=True)
        products_count = products.count()
    context = {'products': products, 'products_count': products_count}
    return render(request, 'store/store.html', context)

def product_detail(request, category_slug, product_slug):
    try:
        product = Product.objects.get(category__slug=category_slug, slug=product_slug)
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=product).exists()
    except Exception as e:
        raise e
    context = {
        'product':product,
        'in_cart': in_cart
    }
    return render(request, 'store/product-detail.html', context)