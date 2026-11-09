from rest_framework.viewsets import ModelViewSet

from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer

from .permissions import IsAdminOrReadOnly

#for serch and filter
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from .filters import ProductFilter


class CategoryViewSet(ModelViewSet):

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]

class ProductViewSet(ModelViewSet):

    queryset = Product.objects.select_related('category').all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]


filter_backends = [
    DjangoFilterBackend,
    SearchFilter,
    OrderingFilter,
]

filterset_class = ProductFilter

#for search others for filter
search_fields = [
    'name',
    'description',
    'category__name',
]

ordering_fields = [
    'price',
    'created_at',
    'name',
]

ordering = ['-created_at']