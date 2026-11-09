from django.contrib import admin

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'order_number',
        'user',
        'status',
        'total_price',
        'created_at',
    )

    search_fields = (
        'order_number',
        'user__username',
        'recipient_name',
        'phone_number',
    )

    list_filter = (
        'status',
        'created_at',
    )

    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = (
        'Order',
        'product_name',
        'product_sku',
        'unit_price',
        'quantity',
    )

    search_fields = (
        'product_name',
        'product_sku',
    )