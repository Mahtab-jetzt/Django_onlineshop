
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
    payment_info = Payment.objects.only(
        'order_id'
    ).get(pk=payment_id)

    order = Order.objects.select_for_update().get(
        pk=payment_info.order_id
    )

    payment = Payment.objects.select_for_update().get(
        pk=payment_id,
        order=order
    )

    if payment.status == Payment.Status.SUCCESSFUL:
        return payment

    if payment.status == Payment.Status.REFUNDED:
        raise ValidationError(
            'This payment has already been refunded.'
        )

    if payment.status != Payment.Status.PENDING:
        raise ValidationError(
            'This payment is not pending.'
        )

    if order.payments.filter(
        status=Payment.Status.SUCCESSFUL
    ).exclude(pk=payment.pk).exists():
        raise ValidationError(
            'Another payment for this order is already successful.'
        )

    payment.status = Payment.Status.SUCCESSFUL
    payment.transaction_id = transaction_id
    payment.paid_at = timezone.now()

    payment.save(update_fields=[
        'status',
        'transaction_id',
        'paid_at',
        'updated_at'
    ])

    if order.status == Order.Status.PENDING:
        order.status = Order.Status.PROCESSING
        order.save(update_fields=[
            'status',
            'updated_at'
        ])

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
