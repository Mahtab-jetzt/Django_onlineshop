from django.db import models
import uuid
from django.core.validators import RegexValidator

phone_number_validator = RegexValidator(
    regex=r'^09\d{9}$',
    message='Enter a valid mobile number.'
)

postal_code_validator = RegexValidator(
    regex=r'^\d{10}$',
    message='Postal code must contain exactly 10 digits.'
)

class Order(models.Model):

    class Status(models.TextChoices):
    # pending for database and Pending for frontend
        PENDING = 'pending', 'Pending'
        PROCESSING = 'processing', 'Processing'
        SHIPPED = 'shipped', 'Shipped'
        DELIVERED = 'delivered', 'Delivered'
        CANCELLED = 'cancelled', 'Cancelled'

    #a user can have multiple orders
    user = models.ForeignKey(
        'users.user',
        on_delete=models.PROTECT,
        related_name='orders'
    )

    #a unique code for each order
    order_number = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False
    )

    #man status ro faghat tarif kardam vali inja anjam mishe
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )

    #total order price in toman 
    total_price = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        default=0
    )

    #user information saved at checkout
    recipient_name = models.CharField(max_length=150)

    phone_number = models.CharField(
        max_length=11,
        validators=[phone_number_validator]
        )

    shipping_address = models.TextField()

    postal_code = models.CharField(
        max_length=20,
        validators=[postal_code_validator]
        )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(total_price__gte=0),
                name='order_total_price_gte_zero'
            ),
            models.CheckConstraint(
                condition=models.Q(status__in=[
                    'pending',
                    'processing',
                    'shipped',
                    'delivered',
                    'cancelled'
                ]),
                name='order_status_valid'
            ),
        ]

    def clean(self):
        super().clean()

        if not self.recipient_name or not self.recipient_name.strip():
            from django.core.exceptions import ValidationError
            raise ValidationError({
                'recipient_name': 'Recipient name cannot be empty.'
            })

        if not self.shipping_address or not self.shipping_address.strip():
            from django.core.exceptions import ValidationError
            raise ValidationError({
                'shipping_address': 'Shipping address cannot be empty.'
            })


    def __str__(self):
        return f"Order {self.order_number}"

class OrderItem(models.Model):
    #each order has multiple orderitems 
    Order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )

    #each product can have multiple orderitems(order item is a table in database)
    #ex. 2 people buying the same procut at the same time
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.PROTECT,
        related_name='order_items'
    )

    #information saved at purchase time.
    #so the recipt stays the same even after future updates
    product_name = models.CharField(max_length=200)
    product_sku = models.CharField(max_length=50)

    # Price per unit at the time of purchase.
    unit_price = models.DecimalField(
        max_digits=12,
        decimal_places=0
    )


    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(quantity__gte=1),
                name='order_item_quantity_gte_1'
            ),
            models.CheckConstraint(
                condition=models.Q(unit_price__gt=0),
                name='order_item_unit_price_gt_zero'
            ),
        ]

    def __str__(self):
        return f"{self.product_name} x {self.quantity}"

