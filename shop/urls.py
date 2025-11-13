from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import CategoryGetViewSet, ProductGetViewSet, OrderViewSet
from .payment_views import InitiateShopPaymentAPIView, ShopPaymentCallbackAPIView

router = DefaultRouter()
router.register(r'categories', CategoryGetViewSet, basename='category')
router.register(r'products', ProductGetViewSet, basename='product')
router.register(r'orders', OrderViewSet, basename='order')

urlpatterns = [
    path('', include(router.urls)),
    path('payments/initiate/', InitiateShopPaymentAPIView.as_view(), name='shop-payment-initiate'),
    path('payments/callback/', ShopPaymentCallbackAPIView.as_view(), name='shop-payment-callback'),
]
