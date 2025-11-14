from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import CategoryGetViewSet, ProductGetViewSet, OrderViewSet
from .payment_views import PayWithAccountAPIView

router = DefaultRouter()
router.register(r'categories', CategoryGetViewSet, basename='category')
router.register(r'products', ProductGetViewSet, basename='product')
router.register(r'orders', OrderViewSet, basename='order')

urlpatterns = [
    path('', include(router.urls)),
    path('payments/pay_with_account/', PayWithAccountAPIView.as_view(), name='shop-pay-with-account'),
]
