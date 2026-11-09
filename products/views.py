from rest_framework.viewsets import ModelViewSet

from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer


class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ProductViewSet(ModelViewSet):

    queryset = Product.objects.select_related('category').all()

    serializer_class = ProductSerializer

