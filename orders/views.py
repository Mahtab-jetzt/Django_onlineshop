
from django.db import transaction
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError

from cart.models import cart
from .models import Order, OrderItem
from .serializers import CheckoutSerializer, OrderSerializer

from products.models import Product

from rest_framework.response import Response


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

        # Lock cart items while processing the checkout
        cart_items = list(
            user_cart.items.select_related('product').all()
        )

        if not cart_items:
            raise ValidationError({
                'cart': 'Your cart is empty.'
            })

        # Collect product IDs from the cart
        product_ids = [item.product_id for item in cart_items]

        # Lock product rows to prevent concurrent stock updates
        locked_products = Product.objects.select_for_update().filter(
            id__in=product_ids
        ).order_by('id')

        # Build a dictionary for quick product lookup
        products = {
            product.id: product
            for product in locked_products
        }

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

    
        # Create the main order using validated shipping information
        order = Order.objects.create(
            user=request.user,
            total_price=total_price,
            recipient_name=serializer.validated_data['recipient_name'],
            phone_number=serializer.validated_data['phone_number'],
            shipping_address=serializer.validated_data['shipping_address'],
            postal_code=serializer.validated_data['postal_code'],
        )

        
        # Create one OrderItem for each product in the cart
        for item in user_cart.items.select_related('product').all():
            product = item.product

            #snapshot 
            OrderItem.objects.create(
                Order=order,
                product=product,
                product_name=product.name,
                product_sku=product.sku,
                unit_price=product.price,
                quantity=item.quantity,
            )

            #reduce stock after purchase
            product.stock -= item.quantity

            #save the updated stock
            product.save(update_fields=['stock'])

            #empty the cart after purchase
            user_cart.items.all().delete()
        
        # Return the successful order information to the customer
        return Response(
            {
                'message': 'Your order was created successfully.',
                'order_id': order.id,
                'order_number': str(order.order_number),
                'total_price': str(order.total_price),
                'status': order.status,
            },
            status=status.HTTP_201_CREATED
        )

    
class OrderHistoryView(generics.ListAPIView):
    # Use the serializer that displays order details
    serializer_class = OrderSerializer

    # Only authenticated users can view their orders
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Return only orders belonging to the logged-in user
        return Order.objects.filter(
            user=self.request.user
        ).prefetch_related('items').order_by('-created_at')


class OrderDetailView(generics.RetrieveAPIView):
    # Serializer used to display the complete order details
    serializer_class = OrderSerializer

    # Only authenticated users can view order details
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Return only orders belonging to the logged-in user
        return Order.objects.filter(
            user=self.request.user
        ).prefetch_related('items')


