from .models import CartItem, Cart
from .views import _cart_id
def cart_items_count(request):
    if 'admin' in request.path:
        return {}
    else:
        try:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart__cart_id = cart, is_active=True)
            count=0
            for cart_item in cart_items:
                count += cart_item.quantity
        except Cart.DoesNotExist:
            count=0
    return dict(count=count)