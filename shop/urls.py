from rest_framework.routers import DefaultRouter
from .views import CategoryGetViewSet, ProductGetViewSet

router = DefaultRouter()
router.register(r'categories', CategoryGetViewSet, basename='category')
router.register(r'products', ProductGetViewSet, basename='product')

urlpatterns = router.urls
