from django.contrib import admin
from django.utils.html import format_html
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'price', 'quantity', 'get_cost']
    fields = ['product', 'price', 'quantity', 'get_cost']

    def get_cost(self, obj):
        return f"{obj.get_cost()} ₽"

    get_cost.short_description = 'Стоимость'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'customer_name',
        'customer_phone',
        'status_badge',
        'total_price_display',
        'created_at',
        'user_display'
    ]
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['customer_name', 'customer_phone', 'delivery_address']
    readonly_fields = ['created_at', 'updated_at', 'total_price', 'status_timeline']
    inlines = [OrderItemInline]
    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'session_key', 'status', 'total_price', 'created_at', 'updated_at')
        }),
        ('Информация о клиенте', {
            'fields': ('customer_name', 'customer_phone', 'customer_email')
        }),
        ('Доставка', {
            'fields': ('delivery_address', 'delivery_time', 'payment_method')
        }),
        ('Дополнительно', {
            'fields': ('comment', 'status_timeline'),
            'classes': ('collapse',)
        }),
    )
    actions = ['mark_confirmed', 'mark_processing', 'mark_in_progress', 'mark_delivered', 'mark_cancelled']

    def status_badge(self, obj):
        colors = {
            'new': 'secondary',
            'confirmed': 'primary',
            'processing': 'info',
            'in_progress': 'warning',
            'delivered': 'success',
            'cancelled': 'danger',
        }
        return format_html(
            '<span class="badge bg-{}">{}</span>',
            colors.get(obj.status, 'secondary'),
            obj.get_status_display()
        )

    status_badge.short_description = 'Статус'

    def total_price_display(self, obj):
        return f"{obj.total_price} ₽"

    total_price_display.short_description = 'Сумма'

    def user_display(self, obj):
        if obj.user:
            return obj.user.username
        return 'Гость'

    user_display.short_description = 'Пользователь'

    def status_timeline(self, obj):
        timeline = obj.get_status_timeline()
        html = '<div class="status-timeline">'
        for step in timeline:
            icon = '✓' if step['completed'] else '○'
            color = 'text-success' if step['completed'] else 'text-muted'
            active = 'fw-bold' if step['active'] else ''
            html += f'<div class="{color} {active}">{icon} {step["name"]}</div>'
        html += '</div>'
        return format_html(html)

    status_timeline.short_description = 'Временная шкала статусов'

    def mark_confirmed(self, request, queryset):
        queryset.update(status='confirmed')

    mark_confirmed.short_description = "Перевести в статус 'Подтвержден'"

    def mark_processing(self, request, queryset):
        queryset.update(status='processing')

    mark_processing.short_description = "Перевести в статус 'Обработан'"

    def mark_in_progress(self, request, queryset):
        queryset.update(status='in_progress')

    mark_in_progress.short_description = "Перевести в статус 'Доставляется'"

    def mark_delivered(self, request, queryset):
        queryset.update(status='delivered')

    mark_delivered.short_description = "Перевести в статус 'Доставлен'"

    def mark_cancelled(self, request, queryset):
        queryset.update(status='cancelled')

    mark_cancelled.short_description = "Перевести в статус 'Отменен'"

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ['user', 'session_key']
        return self.readonly_fields


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity', 'price', 'get_cost']
    list_filter = ['order__status']

    def get_cost(self, obj):
        return f"{obj.get_cost()} ₽"

    get_cost.short_description = 'Стоимость'