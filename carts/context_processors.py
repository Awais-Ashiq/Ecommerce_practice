from .models import CartItem, Cart
from .views import _cart_id
def cart_items_count(request):
    if 'admin' in request.path:
        return {}
    else:
        try:
            if request.user.is_authenticated:
                cart_items = CartItem.objects.all().filter(user=request.user)
            else:
                cart = Cart.objects.get(cart_id=_cart_id(request))
                cart_items = CartItem.objects.all().filter(cart=cart, is_active=True)
            count=0
            for cart_item in cart_items:
                count += cart_item.quantity
        except Cart.DoesNotExist:
            count=0
    return dict(count=count)