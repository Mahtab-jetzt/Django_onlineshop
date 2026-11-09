from rest_framework import serializers

from .models import cart, CartItem
from products.models import Product
from products.serializers import ProductSerializer


class CartItemSerializer(serializers.ModelSerializer):

    product = ProductSerializer(read_only=True)

    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source='product',
        write_only=True
    )

    class Meta:
        model = CartItem

        fields = [
            'id',
            'product',
            'product_id',
            'quantity',
            'created_at',
            'updated_at',
        ]

        read_only_fields = [
            'id',
            'created_at',
            'updated_at',
        ]


class CartSerializer(serializers.ModelSerializer):
    #display all items on the cart
    items = CartItemSerializer(many=True, read_only=True)

    #calculate the total price on server
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = cart

        fields = [
            'id',
            'user',
            'items',
            'total_price',
            'created_at',
            'updated_at',
        ]

        read_only_fields = [
            'id',
            'user',
            'total_price',
            'created_at',
            'updated_at',
        ]

    def get_total_price(self, obj):
        total = 0

        for item in obj.items.select_related('product').all():
            total += item.product.price*item.quantity
            return total
