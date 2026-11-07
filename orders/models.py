from django.db import models
import uuid

class Order(models.Model):

    class Status(models.TextChoices):
    # pending for database and Pending for frontend
        PENDING = 'pending', 'Pending'
        PROCESSING = 'processing', 'Processing'
        SHIPPED = 'shipped', 'Shipped'
        DELIVERD = 'deliverd', 'Deliverd'
        CANCELLED = 'cancelled', 'Cancelled'

    #a user can have multiple orders
    user = models.ForeignKey(
        'users.User',
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
    phone_number = models.CharField(max_length=11)
    shipping_address = models.TextField()
    postal_video = models.CharField(max_length=20)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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
            related_name='Order_items'
        )

    #purchase time
        product_name = models.CharField(max_length=200)
        product_sku = models.CharField(max_length=50)

        unit_price = models.DecimalField(
            max_digits=12,
            decimal_places=0
        )

        quantity = models.PositiveIntegerField()

        def __str__(self):
            return f"{self.product_name} x {self.quantity}"

