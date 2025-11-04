from rest_framework import viewsets, permissions, mixins
from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer

class ProductListRetriveViewSet(mixins.ListModelMixin,mixins.RetrieveModelMixin,viewsets.GenericViewSet):
	pass

class CategoryViewSet(viewsets.ModelViewSet):
	queryset = Category.objects.all()
	serializer_class = CategorySerializer
	permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class ProductViewSet(viewsets.ModelViewSet):
	queryset = Product.objects.all()
	serializer_class = ProductSerializer
	permission_classes = [permissions.IsAuthenticatedOrReadOnly]



class CategoryGetViewSet(ProductListRetriveViewSet):
	queryset = Category.objects.all()
	serializer_class = CategorySerializer


class ProductGetViewSet(ProductListRetriveViewSet):
	queryset = Product.objects.filter(is_available=True)
	serializer_class = ProductSerializer

