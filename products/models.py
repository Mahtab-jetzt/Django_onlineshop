from django.db import models
from django.core.exceptions import ValidationError

import uuid
from django.utils.text import slugify
#for image
from django.core.validators import FileExtensionValidator
from PIL import Image

#1
def generate_sku():
    return f"PRD-{uuid.uuid4().hex.upper()}"

#2
def generate_unique_slug(instance, value):
    max_length = instance._meta.get_field('slug').max_length

    base_slug = slugify(value, allow_unicode=True) or 'product'
    slug = base_slug[:max_length]
    counter = 1

    while instance.__class__.objects.filter(
        slug=slug
    ).exclude(pk=instance.pk).exists():

        counter += 1
        suffix = f'-{counter}'
        slug = f'{base_slug[:max_length - len(suffix)]}{suffix}'

    return slug

#3 for image

def validate_image_size(image):
    max_size = 1 * 1024 * 1024

    if image.size > max_size:
        raise ValidationError(
            'Image size cannot exceed 1 MB.'
        )

#4 for image

def validate_image_format(image):
    try:
        image.seek(0)

        with Image.open(image) as img:
            if img.format not in ['JPEG', 'PNG', 'WEBP']:
                raise ValidationError(
                    'Only JPEG, PNG and WebP images are allowed.'
                )

            img.verify()

    except ValidationError:
        image.seek(0)
        raise

    except Exception:
        image.seek(0)
        raise ValidationError(
            'The uploaded file is not a valid image.'
        )

class Category(models.Model):

    name = models.CharField(
        max_length=100,
        unique=True
    )

    slug = models.SlugField(
        max_length=120,
        unique=True,
        allow_unicode=True
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

    class Meta:
            constraints = [
                models.CheckConstraint(
                    condition=~models.Q(parent=models.F('id')),
                    name='category_cannot_be_its_own_parent'
                )
            ]
    
    def clean(self):
        super().clean()
    
        parent = self.parent
        visited = set()
    
        while parent is not None:
            if parent.pk == self.pk:
                raise ValidationError({
                    'parent': 'a category cannot be its own ancestor'
                })
    
            if parent.pk in visited:
                raise ValidationError({
                    'parent': 'circular category hierarchy detected'
                })
    
            visited.add(parent.pk)
            parent = parent.parent
    
                
    def __str__(self):
        return self.name

class Product(models.Model):

    name = models.CharField(
        max_length=200
    )

    slug = models.SlugField(
        max_length=220,
        unique=True,
        blank=True,
        allow_unicode=True
    )

    sku = models.CharField(
        max_length=36,
        unique=True,
        default=generate_sku,
        editable=False
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

    
    def clean(self):
        super().clean()

        if self.is_active and self.category_id:
            if not self.category.is_active:
                raise ValidationError({
                    'category': 'An active product cannot belong to an inactive category.'
                }) 
        

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(self, self.name)
            if kwargs.get('update_fields') is not None and kwargs['update_fields']:
                kwargs['update_fields'] = set(kwargs['update_fields']) | {'slug'}

        super().save(*args, **kwargs)


    def __str__(self):
        return self.name

class ProductImage(models.Model):
    
    product = models.ForeignKey(
        Product,
        on_delete = models.CASCADE,
        related_name= 'images',
    )

    image = models.ImageField(
        upload_to='products/%Y/%m/',
        validators=[
            FileExtensionValidator(
                allowed_extensions=['jpg', 'jpeg', 'png', 'webp']
            ),
            validate_image_size,
            validate_image_format,
        ]
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