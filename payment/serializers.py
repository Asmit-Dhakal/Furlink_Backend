from rest_framework import serializers
from .models import Transaction


class InitiatePaymentSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    product_code = serializers.CharField(max_length=64, required=False, default='EPAYTEST')
    transaction_uuid = serializers.CharField(max_length=128, required=False, allow_blank=True)
    success_url = serializers.URLField(required=False, allow_blank=True)
    failure_url = serializers.URLField(required=False, allow_blank=True)
    currency = serializers.CharField(max_length=8, required=False, default='NPR')


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'tx_uuid', 'amount', 'currency', 'status', 'signature', 'raw_response', 'created_at']