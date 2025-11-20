from django.db import models

# Create your models here.

from django.db import models
from django.contrib.auth.models import User
from catalog.models import Product


class Order(models.Model):
    STATUS_CHOICES = [
        ('new', 'Новый'),
        ('confirmed', 'Подтвержден'),
        ('in_progress', 'В процессе доставки'),
        ('delivered', 'Доставлен'),
        ('cancelled', 'Отменен'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='new',
        verbose_name='Статус'
    )
    delivery_address = models.TextField(verbose_name='Адрес доставки')
    delivery_time = models.DateTimeField(verbose_name='Время доставки')
    customer_phone = models.CharField(max_length=20, verbose_name='Телефон клиента')
    customer_name = models.CharField(max_length=100, verbose_name='Имя клиента')
    comment = models.TextField(blank=True, verbose_name='Комментарий')

    def __str__(self):
        return f"Заказ #{self.id} - {self.customer_name}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"