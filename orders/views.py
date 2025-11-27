from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.db import transaction
from catalog.models import Product
from .cart import Cart
from .forms import OrderForm
from .models import Order, OrderItem


def cart_detail(request):
    cart = Cart(request)
    return render(request, 'orders/cart_detail.html', {'cart': cart})


@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)

    quantity = int(request.POST.get('quantity', 1))
    cart.add(product=product, quantity=quantity)

    messages.success(request, f'Товар "{product.name}" добавлен в корзину')
    return redirect('orders:cart_detail')


@require_POST
def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)

    messages.success(request, f'Товар "{product.name}" удален из корзины')
    return redirect('orders:cart_detail')


@require_POST
def cart_update(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)

    quantity = int(request.POST.get('quantity', 1))
    if quantity > 0:
        cart.add(product=product, quantity=quantity, update_quantity=True)
        messages.success(request, f'Количество товара "{product.name}" обновлено')
    else:
        cart.remove(product)

    return redirect('orders:cart_detail')


def order_create(request):
    cart = Cart(request)

    if len(cart) == 0:
        messages.warning(request, 'Ваша корзина пуста')
        return redirect('catalog:product_list')

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    order = form.save(commit=False)

                    # Если пользователь авторизован, связываем заказ с ним
                    if request.user.is_authenticated:
                        order.user = request.user

                    # Сохраняем ключ сессии для неавторизованных пользователей
                    if not request.user.is_authenticated:
                        order.session_key = request.session.session_key

                    order.save()

                    # Создаем элементы заказа
                    for item in cart:
                        OrderItem.objects.create(
                            order=order,
                            product=item['product'],
                            price=item['price'],
                            quantity=item['quantity']
                        )

                    # Обновляем общую стоимость
                    order.update_total_price()

                    # Очищаем корзину
                    cart.clear()

                    messages.success(request, 'Ваш заказ успешно создан!')
                    return redirect('orders:order_created', order_id=order.id)

            except Exception as e:
                messages.error(request, f'Произошла ошибка при создании заказа: {str(e)}')

    else:
        # Предзаполняем форму данными пользователя, если он авторизован
        initial_data = {}
        if request.user.is_authenticated:
            initial_data = {
                'customer_name': f"{request.user.first_name} {request.user.last_name}".strip(),
                'customer_email': request.user.email,
                'customer_phone': getattr(request.user.profile, 'phone', ''),
            }

        form = OrderForm(initial=initial_data)

    return render(request, 'orders/order_create.html', {
        'cart': cart,
        'form': form
    })


def order_created(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'orders/order_created.html', {'order': order})


@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders/order_list.html', {'orders': orders})


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/order_detail.html', {'order': order})