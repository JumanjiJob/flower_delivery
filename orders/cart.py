from decimal import Decimal
from catalog.models import Product


class Cart:
    def __init__(self, request):
        """
        Инициализация корзины
        """
        self.request = request
        self.session = request.session
        cart = self.session.get('cart')
        if not cart:
            cart = self.session['cart'] = {}
        self.cart = cart

    def add(self, product, quantity=1, update_quantity=False):
        """
        Добавить продукт в корзину или обновить его количество
        """
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {
                'quantity': 0,
                'price': str(product.price)
            }

        if update_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity

        self.save()

    def save(self):
        """
        Сохранить корзину в сессии
        """
        self.session['cart'] = self.cart
        self.session.modified = True

    def remove(self, product):
        """
        Удалить продукт из корзины
        """
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def __iter__(self):
        """
        Перебор элементов в корзине и получение продуктов из базы данных
        """
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        cart = self.cart.copy()

        for product in products:
            cart[str(product.id)]['product'] = product

        for item in cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self):
        """
        Подсчет всех товаров в корзине
        """
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        """
        Подсчет стоимости товаров в корзине
        """
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

    def clear(self):
        """
        Очистка корзины
        """
        del self.session['cart']
        self.session.modified = True

    def get_cart_items(self):
        """
        Получить элементы корзины с объектами продуктов
        """
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)

        cart_items = []
        for product in products:
            product_id = str(product.id)
            cart_items.append({
                'product': product,
                'quantity': self.cart[product_id]['quantity'],
                'price': Decimal(self.cart[product_id]['price']),
                'total_price': Decimal(self.cart[product_id]['price']) * self.cart[product_id]['quantity']
            })

        return cart_items