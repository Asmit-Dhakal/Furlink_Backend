from rest_framework import viewsets, permissions

from .models import Pet, Adoption, Category, AdoptionPrice
from .serializers import (
    PetSerializer, AdoptionSerializer, CategorySerializer, AdoptionPriceSerializer
)


class PetViewSet(viewsets.ModelViewSet):
    """CRUD for Pet."""
    permission_classes = [permissions.IsAuthenticated]
    queryset = Pet.objects.all()
    serializer_class = PetSerializer


class AdoptionViewSet(viewsets.ModelViewSet):
    """Manage adoptions. Only authenticated users can create/update."""
    permission_classes = [permissions.IsAuthenticated]
    queryset = Adoption.objects.all()
    serializer_class = AdoptionSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class AdoptionPriceViewSet(viewsets.ModelViewSet):
    """Manage adoption prices. Support filtering by category and adopter via query params."""
    permission_classes = [permissions.IsAuthenticated]
    queryset = AdoptionPrice.objects.all()
    serializer_class = AdoptionPriceSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        category_id = self.request.query_params.get('category')
        adopter_id = self.request.query_params.get('adopter')
        active = self.request.query_params.get('active')
        if category_id:
            qs = qs.filter(category_id=category_id)
        if adopter_id:
            qs = qs.filter(adopter_id=adopter_id)
        if active is not None:
            if active.lower() in ('1', 'true', 'yes'):
                qs = qs.filter(is_active=True)
            elif active.lower() in ('0', 'false', 'no'):
                qs = qs.filter(is_active=False)
        return qs
