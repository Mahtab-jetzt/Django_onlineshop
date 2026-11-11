#search is pre-available in DRF , I added it in views.py 
import django_filters

from .models import Product


class ProductFilter(django_filters.FilterSet):
    # Filter products with a minimum price (price >= min_price)
    min_price = django_filters.NumberFilter(
        field_name='price',
        lookup_expr='gte'
    )

    # Filter products with a maximum price (price <= max_price)
    max_price = django_filters.NumberFilter(
        field_name='price',
        lookup_expr='lte'
    )

    class Meta:
        model = Product

        # Fields available for exact filtering
        fields = [
            'category',
            'is_active',
        ]

    