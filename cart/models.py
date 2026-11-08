from django.db import models
from django.core.exceptions import ValidationError

class cart(models.Model):
#each user can only have one cart

    user = models.OneToOneField(
        'users.user',
        on_delete=models.CASCADE,
        related_name= 'cart'
        )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Cart"

class CartItem(models.Model):

#each cart can contain multiple cartitems(products)
    cart = models.ForeignKey(
        cart,
        on_delete=models.CASCADE,
        related_name='items'
    )    

#the same product can contain in multiple carts
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.PROTECT,
        related_name='cart_items'
        )

#user and product khodam tarahi kardam pas neveshtam products.Product jaye product


    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [

            models.UniqueConstraint(
                fields=['cart','product'],
                name='unique_product_per_cart'
            ),

            models.CheckConstraint(
                condition= models.Q(quantity__gte=1),
                name='cart_item_quantity_gte_1'
            ),
        ]

    def clean(self):
        super().clean()

        if not self.product_id:
            return

        if not self.product.is_active:
            raise ValidationError({
                'product': 'This product is not available.'
            })

        if self.quantity and self.quantity > self.product.stock:
            raise ValidationError({
                'quantity': 'Requested quantity exceeds available stock.'
            })

    def __str__(self):
        return f'{self.product.name} x {self.quantity}'

