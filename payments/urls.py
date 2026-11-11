from django.urls import path

from .views import PaymentStartView, PaymentVerifyView


urlpatterns = [
    # Start payment for a specific order.
    path(
        'start/<int:order_id>/',
        PaymentStartView.as_view(),
        name='payment-start',
    ),

    # Receive the callback from Zarinpal.
    path(
        'verify/',
        PaymentVerifyView.as_view(),
        name='payment-verify',
    ),
]