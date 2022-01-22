from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.core.paginator import Paginator
from django.db.models import Q
from carts.models import CartItem
from store.models import Product

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