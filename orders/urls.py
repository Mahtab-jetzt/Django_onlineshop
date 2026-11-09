from django.urls import path

from .views import CheckoutView, OrderHistoryView, OrderDetailView

urlpatterns = [
    # Create a new order
    path('checkout/', CheckoutView.as_view(), name='checkout'),

    # View the logged-in user's order history
    path('history/', OrderHistoryView.as_view(), name='order-history'),

    # View details of a specific order
        path('<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
]

