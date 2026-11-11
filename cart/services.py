
from django.core.exceptions import ValidationError
from django.db import transaction

from .models import cart, CartItem
from products.models import Product


@transaction.atomic
def add_to_cart(user, product_id, quantity=1):

    if quantity < 1:
        raise ValidationError('Quantity must be at least 1.')

    user_cart, _ = cart.objects.get_or_create(user=user)

    user_cart = cart.objects.select_for_update().get(
        pk=user_cart.pk
    )

    product = Product.objects.select_for_update().get(
        pk=product_id
    )

    if not product.is_active:
        raise ValidationError('This product is not available.')

    item = CartItem.objects.filter(
        cart=user_cart,
        product=product
    ).first()

    if item:
        item.quantity += quantity
    else:
        item = CartItem(
            cart=user_cart,
            product=product,
            quantity=quantity
        )

    item.full_clean()
    item.save()

    return item


@transaction.atomic
def update_cart_item_quantity(user, item_id, quantity):

    if quantity < 1:
        raise ValidationError('Quantity must be at least 1.')

    initial_item = CartItem.objects.get(
        pk=item_id,
        cart__user=user
    )

    user_cart = cart.objects.select_for_update().get(
        pk=initial_item.cart_id
    )

    product = Product.objects.select_for_update().get(
        pk=initial_item.product_id
    )

    item = CartItem.objects.select_for_update().get(
        pk=item_id,
        cart=user_cart
    )

    if not product.is_active:
        item.delete()
        return None

    item.quantity = quantity

    item.full_clean()
    item.save(update_fields=['quantity', 'updated_at'])

    return item


@transaction.atomic
def remove_cart_item(user, item_id):

    item = CartItem.objects.get(
        pk=item_id,
        cart__user=user
    )

    item.delete()


@transaction.atomic
def remove_product_from_all_carts(product_id):

    CartItem.objects.filter(
        product_id=product_id
    ).delete()


@transaction.atomic
def validate_cart_before_checkout(user):

    user_cart = cart.objects.select_for_update().get(
        user=user
    )

    initial_items = list(
        CartItem.objects.filter(
            cart=user_cart
        ).values_list('product_id', flat=True)
    )

    products = Product.objects.select_for_update().filter(
        pk__in=initial_items
    ).order_by('pk')

    products_by_id = {
        product.pk: product for product in products
    }

    items = list(
        CartItem.objects.select_for_update().filter(
            cart=user_cart
        ).order_by('product_id')
    )

    valid_items = []

    for item in items:

        product = products_by_id.get(item.product_id)

        if product is None or not product.is_active:
            item.delete()
            continue

        if item.quantity > product.stock:
            raise ValidationError(
                f'Insufficient stock for {product.name}. '
                f'Available stock: {product.stock}.'
            )

        valid_items.append(item)

    return valid_items
