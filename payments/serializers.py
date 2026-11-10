from rest_framework import serializers

from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    # The order number is shown for reference, but cannot be edited.
    order_number = serializers.UUIDField(
        source='order.order_number',
        read_only=True
    )

    class Meta:
        model = Payment

        # Only expose information the client needs to see.
        fields = [
            'id',
            'order_number',
            'amount',
            'provider',
            'status',
            'transaction_id',
            'created_at',
            'paid_at',
        ]

        # The client must not control payment state or gateway identifiers.
        read_only_fields = fields