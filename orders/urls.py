from django.urls import path

from .views import CheckoutView, OrderHistoryView

urlpatterns = [
    # Create a new order
    path('checkout/', CheckoutView.as_view(), name='checkout'),

    # View the logged-in user's order history
    path('history/', OrderHistoryView.as_view(), name='order-history'),
]
