from rest_framework.routers import DefaultRouter

from .views import CategoryViewSet, ProductViewSet, ProductImageViewSet


router = DefaultRouter()

router.register(
    'categories',
    CategoryViewSet,
    basename='category'
)

router.register(
    'products',
    ProductViewSet,
    basename='product'
)

router.register(
    'product_images',
    ProductImageViewSet,
    basename='product_image'
)

urlpatterns = router.urls
