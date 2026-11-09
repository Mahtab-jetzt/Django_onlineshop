from rest_framework import serializers
from .models import Category


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = [
            'id',
            'name',
            'slug',
            'description',
            'parent',
            'is_active',
            'created_at',
            'updated_at',
        ]

        read_only_fields = [
            'id',
            'created_at',
            'updated_at',
        ]

    def validate_parent(self, value):

        if value is None:
            return value

        if self.instance and value.pk == self.instance.pk:
            raise serializers.ValidationError(
                'A category cannot be its own parent.'
            )

        parent = value
        visited = set()

        while parent is not None:

            if self.instance and parent.pk == self.instance.pk:
                raise serializers.ValidationError(
                    'A category cannot be its own ancestor.'
                )

            if parent.pk in visited:
                raise serializers.ValidationError(
                    'Circular category hierarchy detected.'
                )

            visited.add(parent.pk)
            parent = parent.parent

        return value

from .models import Category, Product, ProductImage


class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product

        fields = [
            'id',
            'name',
            'slug',
            'sku',
            'description',
            'price',
            'stock',
            'category',
            'is_active',
            'created_at',
            'updated_at',
        ]

        read_only_fields = [
            'id',
            'slug',
            'sku',
            'created_at',
            'updated_at',
        ]

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                'Price must be greater than zero.'
            )

        return value

    def validate_category(self, value):
        if not value.is_active:
            raise serializers.ValidationError(
                'Products cannot belong to an inactive category.'
            )

        return value