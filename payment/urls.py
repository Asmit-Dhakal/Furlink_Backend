from django.urls import path
from .views import InitiateEsewaPaymentAPIView, EsewaCallbackAPIView, TransactionDetailAPIView

urlpatterns = [
    path('initiate/', InitiateEsewaPaymentAPIView.as_view(), name='payment-initiate'),
    path('callback/', EsewaCallbackAPIView.as_view(), name='payment-callback'),
    path('transaction/<str:tx_uuid>/', TransactionDetailAPIView.as_view(), name='transaction-detail'),
]
