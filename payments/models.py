from django.db import models


class Payment(models.Model):

    class Provider(models.TextChoices):
        ZARINPAL = 'zarinpal', 'Zarinpal'

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        SUCCESSFUL = 'successful', 'Successful'
        FAILED = 'failed', 'Failed'
        REFUNDED = 'refunded', 'Refunded'

    #each order can have multiple payment attempts
    order = models.ForeignKey(
        'orders.Order',
        on_delete=models.PROTECT,
        related_name='payments'
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=0
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )

    #payment gateway information(saved in database)
    Provider = models.CharField(
        max_length=20,
        choices = Provider.choices,
        default= Provider.ZARINPAL
    )

    transaction_id = models.CharField(
        max_length=100,
        blank=True,
        null=True   
    )
 
    paid_at = models.DateTimeField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"payment for order{self.order.order_number}"