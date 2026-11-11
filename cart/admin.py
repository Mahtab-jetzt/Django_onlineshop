from django.contrib import admin

from .models import cart, CartItem


@admin.register(cart)
class CartAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'created_at',
        'updated_at',
    )

    search_fields = (
        'user__username',
        'user__email',
    )


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = (
        'cart',
        'product',
        'quantity',
        'created_at',
    )

    search_fields = (
        'product__name',
        'cart__user__username',
    )