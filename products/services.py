
from django.db import transaction

from .models import Product


@transaction.atomic
def deactivate_product(product_id):

    product = Product.objects.select_for_update().get(
        pk=product_id
    )

    if not product.is_active:
        return product

    product.is_active = False

    product.save(
        update_fields=['is_active', 'updated_at']
    )

    from cart.services import remove_product_from_all_carts

    remove_product_from_all_carts(product.pk)

    return product
