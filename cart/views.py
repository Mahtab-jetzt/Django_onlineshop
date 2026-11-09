from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated

from .models import cart, CartItem
from .serializers import CartSerializer, CartItemSerializer

from rest_framework.response import Response

from django.db import transaction
from rest_framework.exceptions import ValidationError


class CartDetailView(generics.RetrieveAPIView):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        #get the current user cart or create one if it doesnt exist
        user_cart, created = cart.objects.get_or_create(
            user=self.request.user
        )
        return user_cart

class CartItemCreateView(generics.CreateAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def perform_create(self,serializer):
        #get the logged-in user cart
        user_cart, created = cart.objects.get_or_create(
            user = self.request.user
        )

        #get the user requested product and its quantity
        product = serializer.validated_data['product']
        requested_quantity = serializer.validated_data['quantity']
        #lock the product row to prevent cocurrent stock changes
        product = product.objects.select_for_update().get(
            pk = product.pk
        )

        #reject inactive product
        if not product.is_active:
            raise ValidationError({
                'product_id': 'this product is not available'
            })     

        # Find an existing item for this product in the user's cart
        cart_item = CartItem.objects.filter(
            cart=user_cart,
            product=product
        ).first()

        # Calculate the total requested quantity
        total_quantity = requested_quantity

        if cart_item:
            total_quantity += cart_item.quantity

        # Check whether enough stock is available
        if total_quantity > product.stock:
            raise ValidationError({
                'quantity': 'Requested quantity exceeds available stock.'
            })

        # Increase the existing item instead of creating a duplicate
        if cart_item:
            cart_item.quantity = total_quantity
            cart_item.save(update_fields=['quantity', 'updated_at'])

        else:
            # Create a new cart item if the product is not already in the cart
            serializer.save(
                cart=user_cart,
                product=product
            )
    

    def perform_create(self, serializer):
        # Get or create the cart belonging to the logged-in user
        user_cart, created = cart.objects.get_or_create(
            user=self.request.user
        )

        # Save the new cart item inside the user's cart
        serializer.save(cart=user_cart)


class CartItemUpdateView(generics.UpdateAPIView):
    # Use CartItemSerializer to validate and update cart item data
    serializer_class = CartItemSerializer

    # Only authenticated users can update their cart
    permission_classes = [IsAuthenticated]

    # Find the cart item only inside the current user's cart
    def get_queryset(self):
        return CartItem.objects.filter(
            cart__user=self.request.user
        )


class CartItemDeleteView(generics.DestroyAPIView):
    # Use the CartItem model to find the item to delete
    queryset = CartItem.objects.all()

    # No serializer is needed for deleting an item
    permission_classes = [IsAuthenticated]

    # Allow users to delete items only from their own cart
    def get_queryset(self):
        return CartItem.objects.filter(
            cart__user=self.request.user
        )


