from django.urls import path
from .views import CartDetailView, CartItemCreateView, CartItemUpdateView, CartItemDeleteView


urlpatterns = [
    # View the current user's cart
    path('', CartDetailView.as_view(), name='cart-detail'),

    # Add a product to the current user's cart
    path('items/', CartItemCreateView.as_view(), name='cart-item-create'),

    #update the quantity of acart item
    path('items/<int:pk>/', CartItemUpdateView.as_view(), name='cart-item-update'),

    #remove an item from cart
    path('items/<int:pk>/delete/', CartItemDeleteView.as_view(), name='cart-item-delete'),
]

