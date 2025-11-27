from .cart import Cart

def cart(request):
    return {
        'cart_total_items': len(Cart(request)),
        'cart_total_price': Cart(request).get_total_price()
    }