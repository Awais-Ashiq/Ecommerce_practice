from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.core.paginator import Paginator
from django.db.models import Q
from carts.models import CartItem, Cart
from store.models import Product
from django.contrib.auth.decorators import login_required
from carts.views import _cart_id

def store(request, category_slug=None):
    products=None
    if category_slug:
        products = Product.objects.filter(category__slug=category_slug).filter(is_available=True).order_by('id')
        products_count = products.count()
    else:
        products = Product.objects.all().filter(is_available=True).order_by('id')

    paginator = Paginator(products, 3)
    page_number = request.GET.get('page')
    paged_product = paginator.get_page(page_number)
    products_count = products.count()
    context = {'products': paged_product, 'products_count': products_count}
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

def search(request):
    pattern = request.GET['keyword']
    if pattern:
        products = Product.objects.filter(Q(description__icontains=pattern) | Q(product_name__icontains=pattern) | Q(category__category_name__icontains=pattern)).order_by('-created_date')
        products_count = products.count()
    context = {
        'products':products,
        'products_count': products_count
    }
    return render(request, 'store/store.html', context)

@login_required(login_url="login")
def checkout(request, total=0, quantity=0, cart_item=None):
    cart_items_count=0
    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
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
    return render(request, 'store/checkout.html', context)