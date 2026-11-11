from rest_framework.viewsets import ModelViewSet

from .models import Category, Product, ProductImage
from .serializers import CategorySerializer, ProductSerializer, ProductImageSerializer

#permission
from .permissions import IsAdminOrReadOnly

#for serch and filter
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from .filters import ProductFilter

#pagination
from .pagination import ProductPagination

#images 
from rest_framework.parsers import MultiPartParser, FormParser

class CategoryViewSet(ModelViewSet):

    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    permission_classes = [IsAdminOrReadOnly]

class ProductViewSet(ModelViewSet):

    queryset = Product.objects.select_related('category').all()
    serializer_class = ProductSerializer 

    permission_classes = [IsAdminOrReadOnly]

    pagination_class = ProductPagination


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

#images view
class ProductImageViewSet(ModelViewSet):

    # Retrieve images along with their related products
    queryset = ProductImage.objects.select_related('product').all()

    serializer_class = ProductImageSerializer

    # Restrict image modifications to staff users
    permission_classes = [IsAdminOrReadOnly]

    # Support multipart and form-based file uploads
    parser_classes = [MultiPartParser, FormParser]