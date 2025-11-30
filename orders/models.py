from django.db import models
from django.contrib.auth.models import User
from catalog.models import Product
from django.core.validators import MinValueValidator
from django.utils import timezone
from django.urls import reverse


class Order(models.Model):
    STATUS_CHOICES = [
        ('new', '🆕 Новый'),
        ('confirmed', '✅ Подтвержден'),
        ('processing', '🔧 Обработан'),
        ('in_progress', '🚚 Доставляется'),
        ('delivered', '📦 Доставлен'),
        ('cancelled', '❌ Отменен'),
    ]

    PAYMENT_CHOICES = [
        ('cash', '💵 Наличные при получении'),
        ('card', '💳 Онлайн оплата картой'),
        ('transfer', '🏦 Банковский перевод'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        null=True,
        blank=True
    )
    session_key = models.CharField(
        max_length=40,
        verbose_name='Ключ сессии',
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='new',
        verbose_name='Статус'
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_CHOICES,
        default='cash',
        verbose_name='Способ оплаты'
    )
    delivery_address = models.TextField(verbose_name='Адрес доставки')
    delivery_time = models.DateTimeField(verbose_name='Время доставки')
    customer_phone = models.CharField(max_length=20, verbose_name='Телефон клиента')
    customer_name = models.CharField(max_length=100, verbose_name='Имя клиента')
    customer_email = models.EmailField(verbose_name='Email клиента', blank=True)
    comment = models.TextField(blank=True, verbose_name='Комментарий')
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name='Общая стоимость'
    )

    telegram_chat_id = models.BigIntegerField(
        null=True,
        blank=True,
        verbose_name='ID чата Telegram для уведомлений'
    )

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
            models.Index(fields=['user']),
        ]

    def __str__(self):
        return f"Заказ #{self.id} - {self.customer_name}"

    def get_absolute_url(self):
        return reverse('orders:order_detail', kwargs={'order_id': self.id})

    def update_total_price(self):
        """Обновляет общую стоимость заказа"""
        total = sum(item.get_cost() for item in self.items.all())
        self.total_price = total
        self.save()

    def get_status_display_class(self):
        """Возвращает CSS класс для отображения статуса"""
        status_classes = {
            'new': 'bg-secondary',
            'confirmed': 'bg-primary',
            'processing': 'bg-info',
            'in_progress': 'bg-warning',
            'delivered': 'bg-success',
            'cancelled': 'bg-danger',
        }
        return status_classes.get(self.status, 'bg-secondary')

    def get_status_timeline(self):
        """Возвращает временную шкалу статусов"""
        timeline = []
        status_flow = ['new', 'confirmed', 'processing', 'in_progress', 'delivered']

        for status in status_flow:
            timeline.append({
                'status': status,
                'name': dict(self.STATUS_CHOICES)[status],
                'active': status == self.status,
                'completed': status_flow.index(status) < status_flow.index(
                    self.status) if self.status in status_flow else False
            })

        return timeline

    def can_be_cancelled(self):
        """Можно ли отменить заказ"""
        return self.status in ['new', 'confirmed', 'processing']

    def get_items_count(self):
        """Возвращает общее количество товаров в заказе"""
        return sum(item.quantity for item in self.items.all())


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        related_name='items',
        on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name='Товар'
    )
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name='Количество'
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Цена за единицу'
    )

    class Meta:
        verbose_name = 'Элемент заказа'
        verbose_name_plural = 'Элементы заказа'

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

    def get_cost(self):
        """Возвращает общую стоимость позиции"""
        return self.price * self.quantity