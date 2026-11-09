from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated

from .models import cart, CartItem
from .serializers import CartSerializer, CartItemSerializer

from rest_framework.response import Response


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


