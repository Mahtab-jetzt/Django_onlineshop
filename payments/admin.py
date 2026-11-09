from django.contrib import admin

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        'order',
        'amount',
        'provider',
        'status',
        'transaction_id',
        'paid_at',
        'created_at',
    )

    search_fields = (
        'transaction_id',
        'order__order_number',
    )

    list_filter = (
        'status',
        'provider',
        'created_at',
    )

