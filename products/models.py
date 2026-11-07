from django.db import models

class Category(models.Model):

    name = models.CharField(
        max_length=100,
        unique=True
    )

    slug = models.SlugField(
        max_length=120,
        unique=True
    )

    description = models.TextField(
        blank=True
    )

    parent = models.ForeignKey( 
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subcategories'
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Product(models.Model):

    name = models.CharField(
        max_length=200
    )

    slug = models.SlugField(
        max_length=220,
        unique=True
    )

    sku = models.CharField(
        max_length=50,
        unique=True
    )

    description = models.TextField(
        blank=True
    )

    price = models.DecimalField(
        max_digits=12,
        decimal_places=0
    )

    stock = models.PositiveIntegerField(
        default=0
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='products'
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(

        condition=models.Q(price__gt=0),
        name='product_price_gt_zero'
            ),
        ]

    def __str__(self):
        return self.name

class ProductImages(models.Model):
    
    product = models.ForeignKey(
        Product,
        on_delete = models.CASCADE,
        related_name= 'images',
    )

    image = models.ImageField(
        upload_to = 'products/%Y/%m/'
    )

    alt_text = models.CharField(
        max_length=150,
        blank=True
    )

    is_primary = models.BooleanField(
        default=False
    )

    sort_order = models.PositiveIntegerField(
        default=0
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:

        ordering = ['sort_order', 'id'] 

        constraints = [

            models.UniqueConstraint(

                fields=['product'],
                condition = models.Q(is_primary=True),

                name = 'unique_primary_image_per_product'
            )
        ]
        
    def __str__(self):
        return f"{self.product.name} -Image"