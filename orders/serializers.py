
from rest_framework import serializers

from .models import phone_number_validator, postal_code_validator, Order, OrderItem


class CheckoutSerializer(serializers.Serializer):
    # Shipping information provided by the customer
    recipient_name = serializers.CharField(max_length=150)
    phone_number = serializers.CharField(
        max_length=11,
        validators=[phone_number_validator]
    )
    shipping_address = serializers.CharField()
    postal_code = serializers.CharField(
        max_length=10,
        validators=[postal_code_validator]
    )

    def validate_recipient_name(self, value):
        # Reject names containing only whitespace
        if not value.strip():
            raise serializers.ValidationError(
                'Recipient name cannot be empty.'
            )

        return value.strip()

    def validate_shipping_address(self, value):
        # Reject addresses containing only whitespace
        if not value.strip():
            raise serializers.ValidationError(
                'Shipping address cannot be empty.'
            )

        return value.strip()

#order history
class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem

        # Return the purchased product details and price snapshot
        fields = [
            'id',
            'product',
            'product_name',
            'product_sku',
            'unit_price',
            'quantity',
        ]


class OrderSerializer(serializers.ModelSerializer):
    # Include all items belonging to this order
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order

        # Return order information and its purchased items
        fields = [
            'id',
            'order_number',
            'status',
            'total_price',
            'recipient_name',
            'phone_number',
            'shipping_address',
            'postal_code',
            'items',
            'created_at',
        ]
