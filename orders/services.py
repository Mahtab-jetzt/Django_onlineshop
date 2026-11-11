
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import F

from cart.models import cart, CartItem
from products.models import Product

from .models import Order, OrderItem


@transaction.atomic
def create_order_from_cart(
    user,
    recipient_name,
    phone_number,
    shipping_address,
    postal_code
):
    # Lock the user's cart.
    try:
        user_cart = cart.objects.select_for_update().get(user=user)
    except cart.DoesNotExist:
        raise ValidationError('Your cart is empty.')

    # Lock cart items.
    items = list(
        CartItem.objects.select_for_update()
        .filter(cart=user_cart)
        .order_by('product_id')
    )

    if not items:
        raise ValidationError('Your cart is empty.')

    # Lock products in a consistent order.
    product_ids = [item.product_id for item in items]

    products = Product.objects.select_for_update().filter(
        pk__in=product_ids
    ).order_by('pk')

    products_by_id = {
        product.pk: product for product in products
    }

    # Validate products and stock.
    total_price = 0

    for item in items:
        product = products_by_id.get(item.product_id)

        if product is None or not product.is_active:
            raise ValidationError(
                f'{item.product.name} is no longer available.'
            )

        if item.quantity > product.stock:
            raise ValidationError(
                f'Insufficient stock for {product.name}. '
                f'Available stock: {product.stock}.'
            )

        total_price += product.price * item.quantity

    # Validate shipping information.
    order = Order(
        user=user,
        recipient_name=recipient_name,
        phone_number=phone_number,
        shipping_address=shipping_address,
        postal_code=postal_code,
        total_price=total_price
    )

    order.full_clean()
    order.save()

    # Create order items and decrease stock.
    for item in items:
        product = products_by_id[item.product_id]

        OrderItem.objects.create(
            order=order,
            product=product,
            product_name=product.name,
            product_sku=product.sku,
            unit_price=product.price,
            quantity=item.quantity
        )

        product.stock -= item.quantity
        product.save(update_fields=['stock', 'updated_at'])

    # Clear the cart after successful order creation.
    CartItem.objects.filter(cart=user_cart).delete()

    return order


@transaction.atomic
def cancel_order(user, order_id):

    # Lock the order.
    try:
        order = Order.objects.select_for_update().get(
            pk=order_id,
            user=user
        )
    except Order.DoesNotExist:
        raise ValidationError('Order not found.')

    # Only pending orders can be cancelled.
    if order.status != Order.Status.PENDING:
        raise ValidationError(
            'Only pending orders can be cancelled.'
        )

    items = list(
        OrderItem.objects.filter(order=order).order_by('product_id')
    )

    product_ids = [item.product_id for item in items]

    products = Product.objects.select_for_update().filter(
        pk__in=product_ids
    ).order_by('pk')

    products_by_id = {
        product.pk: product for product in products
    }

    # Restore stock.
    for item in items:
        product = products_by_id.get(item.product_id)

        if product is not None:
            product.stock = F('stock') + item.quantity
            product.save(update_fields=['stock', 'updated_at'])

    # Update order status.
    order.status = Order.Status.CANCELLED
    order.save(update_fields=['status', 'updated_at'])

    return order
