from .models import CartItem
from .views import _cart_id
def cart_items_count(request):
    # cart = Cart.objects.get(cart_id=_cart_id(request))
    cart_items = CartItem.objects.filter(cart__cart_id = _cart_id(request), is_active=True)
    count=0
    for cart_item in cart_items:
        count += cart_item.quantity
    return dict(count=count)