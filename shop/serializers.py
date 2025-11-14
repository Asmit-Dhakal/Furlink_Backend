from rest_framework import serializers
from .models import Category, Product, Order, OrderItem, ShopPayment
from decimal import Decimal
from django.db.models import Sum


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'created_at', 'updated_at']


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        write_only=True, queryset=Category.objects.all(), source='category'
    )

    class Meta:
        model = Product
        fields = [
            'id', 'category', 'category_id', 'name', 'price', 'discount_price',
            'description', 'image', 'is_available', 'created_at', 'updated_at'
        ]


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'unit_price', 'created_at', 'line_total']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    items_input = serializers.ListField(write_only=True, required=False,
                                       child=serializers.DictField(), help_text='List of {product_id, quantity, unit_price?}')

    class Meta:
        model = Order
        fields = ['id', 'user', 'total_amount', 'currency', 'status', 'items', 'items_input', 'created_at']
        read_only_fields = ['user', 'total_amount', 'status', 'created_at']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # collapse user to username for brevity
        data['user'] = getattr(instance.user, 'username', None)
        return data


# Simple transaction serializer for account-based payments
class ShopTransactionSerializer(serializers.ModelSerializer):
    order_id = serializers.PrimaryKeyRelatedField(source='order', read_only=True)

    class Meta:
        model = ShopPayment
        fields = ['id', 'order_id', 'user', 'tx_uuid', 'amount', 'currency', 'description', 'created_at']
        read_only_fields = ['tx_uuid', 'created_at']


class CompletedOrderSerializer(serializers.ModelSerializer):
   
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'total_amount', 'currency', 'status', 'items', 'created_at']




