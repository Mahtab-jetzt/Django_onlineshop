
from django.db import transaction
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError

from cart.models import cart
from .models import Order, OrderItem
from .serializers import CheckoutSerializer


class CheckoutView(generics.GenericAPIView):
    # Validate the shipping information sent by the customer
    serializer_class = CheckoutSerializer

    # Only authenticated users can place orders
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        # Validate the customer's shipping information
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Get the logged-in user's cart
        user_cart = cart.objects.prefetch_related(
            'items__product'
        ).filter(user=request.user).first()

        # Reject checkout if the cart does not exist or is empty
        if not user_cart or not user_cart.items.exists():
            raise ValidationError({
                'cart': 'Your cart is empty.'
            })

        # Calculate the order total using current database prices
        total_price = 0

        for item in user_cart.items.all():
            product = item.product

            # Reject inactive products or insufficient stock
            if not product.is_active:
                raise ValidationError({
                    'product': f'{product.name} is not available.'
                })

            if item.quantity > product.stock:
                raise ValidationError({
                    'quantity': f'Not enough stock for {product.name}.'
                })

            total_price += product.price * item.quantity
