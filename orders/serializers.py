
from rest_framework import serializers

from .models import phone_number_validator, postal_code_validator


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
