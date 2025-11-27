from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'price', 'quantity', 'get_cost']

    def get_cost(self, obj):
        return obj.get_cost()

    get_cost.short_description = 'Стоимость'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'customer_name',
        'customer_phone',
        'status',
        'total_price',
        'created_at'
    ]
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['customer_name', 'customer_phone', 'delivery_address']
    readonly_fields = ['created_at', 'total_price']
    inlines = [OrderItemInline]
    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'session_key', 'status', 'total_price', 'created_at')
        }),
        ('Информация о клиенте', {
            'fields': ('customer_name', 'customer_phone', 'customer_email')
        }),
        ('Доставка', {
            'fields': ('delivery_address', 'delivery_time', 'payment_method')
        }),
        ('Дополнительно', {
            'fields': ('comment',),
            'classes': ('collapse',)
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ['user', 'session_key']
        return self.readonly_fields