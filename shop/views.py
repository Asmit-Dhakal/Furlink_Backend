from rest_framework import viewsets, permissions, status,mixins
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db import transaction
from .models import Category, Product, Order, OrderItem
from .serializers import CategorySerializer, ProductSerializer, OrderSerializer, OrderItemSerializer

class ProductListRetriveViewSet(mixins.ListModelMixin,mixins.RetrieveModelMixin,viewsets.GenericViewSet):
	pass





class CategoryGetViewSet(ProductListRetriveViewSet):
	queryset = Category.objects.all()
	serializer_class = CategorySerializer


class ProductGetViewSet(ProductListRetriveViewSet):
	queryset = Product.objects.filter(is_available=True)
	serializer_class = ProductSerializer



class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # users only see their own orders unless staff
        user = self.request.user
        if user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(user=user)

    def create(self, request, *args, **kwargs):
        """Create an Order with nested items input.

        Expected payload: { items: [{product_id, quantity, unit_price?}, ...], currency?: 'USD' }
        """
        items = request.data.get('items') or request.data.get('items_input') or []
        currency = request.data.get('currency') or 'USD'

        if not items or not isinstance(items, list):
            return Response({'detail': 'items list required'}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            order = Order.objects.create(user=request.user, currency=currency)
            for it in items:
                try:
                    product_id = int(it.get('product_id'))
                    qty = int(it.get('quantity', 1))
                except Exception:
                    transaction.set_rollback(True)
                    return Response({'detail': 'invalid product_id or quantity'}, status=status.HTTP_400_BAD_REQUEST)

                try:
                    product = Product.objects.get(pk=product_id)
                except Product.DoesNotExist:
                    transaction.set_rollback(True)
                    return Response({'detail': f'product {product_id} not found'}, status=status.HTTP_404_NOT_FOUND)

                # determine unit price: prefer provided unit_price, else discount_price or price
                if it.get('unit_price') is not None:
                    unit_price = it.get('unit_price')
                else:
                    unit_price = product.discount_price if product.discount_price is not None else product.price

                OrderItem.objects.create(order=order, product=product, quantity=qty, unit_price=unit_price)

            # recalc total and mark paid if desired later when payment confirms
            order.recalc_total()

        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
