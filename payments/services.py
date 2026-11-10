
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from orders.models import Order
from .models import Payment


@transaction.atomic
def create_payment_attempt(user, order_id):
    order = Order.objects.select_for_update().get(
        pk=order_id,
        user=user
    )

    if order.status != Order.Status.PENDING:
        raise ValidationError(
            'This order is not available for payment.'
        )

    if order.total_price <= 0:
        raise ValidationError(
            'Order total price must be greater than zero.'
        )

    if order.payments.filter(
        status=Payment.Status.SUCCESSFUL
    ).exists():
        raise ValidationError(
            'This order has already been paid.'
        )

    payment = Payment(
        order=order,
        amount=order.total_price,
        provider=Payment.Provider.ZARINPAL
    )

    payment.full_clean()
    payment.save()

    return payment

@transaction.atomic
def mark_payment_successful(payment_id, transaction_id):
    # Read the order ID before locking the related records.
    payment_info = Payment.objects.only(
        'order_id'
    ).get(pk=payment_id)

    # Lock the order first to prevent concurrent payment updates.
    order = Order.objects.select_for_update().get(
        pk=payment_info.order_id
    )

    # Lock the payment while updating its status.
    payment = Payment.objects.select_for_update().get(
        pk=payment_id,
        order=order
    )

    # Make the operation idempotent.
    # Repeated callbacks must not update an already successful payment.
    if payment.status == Payment.Status.SUCCESSFUL:
        return payment

    if payment.status == Payment.Status.REFUNDED:
        raise ValidationError(
            'This payment has already been refunded.'
        )

    # Only pending payments can become successful.
    if payment.status != Payment.Status.PENDING:
        raise ValidationError(
            'This payment is not pending.'
        )

    # Prevent a second successful payment for the same order.
    if order.payments.filter(
        status=Payment.Status.SUCCESSFUL
    ).exclude(pk=payment.pk).exists():
        raise ValidationError(
            'Another payment for this order is already successful.'
        )

    # Save the confirmed transaction details.
    payment.status = Payment.Status.SUCCESSFUL
    payment.transaction_id = transaction_id
    payment.paid_at = timezone.now()

    payment.save(update_fields=[
        'status',
        'transaction_id',
        'paid_at',
        'updated_at'
    ])

    # Move a pending order to processing after successful payment.
    if order.status == Order.Status.PENDING:
        order.status = Order.Status.PROCESSING
        order.save(update_fields=[
            'status',
            'updated_at'
        ])

    # If an order was cancelled before the callback arrived,
    # keep its cancelled status. The successful payment must still
    # be recorded and handled separately for a possible refund.

    return payment

@transaction.atomic
def mark_payment_failed(payment_id, transaction_id=None):
    payment_info = Payment.objects.only(
        'order_id'
    ).get(pk=payment_id)

    Order.objects.select_for_update().get(
        pk=payment_info.order_id
    )

    payment = Payment.objects.select_for_update().get(
        pk=payment_id
    )

    if payment.status == Payment.Status.FAILED:
        return payment

    if payment.status in [
        Payment.Status.SUCCESSFUL,
        Payment.Status.REFUNDED
    ]:
        raise ValidationError(
            'A successful or refunded payment cannot be marked as failed.'
        )

    payment.status = Payment.Status.FAILED

    if transaction_id:
        payment.transaction_id = transaction_id

    payment.save(update_fields=[
        'status',
        'transaction_id',
        'updated_at'
    ])

    return payment
