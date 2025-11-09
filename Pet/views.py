
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Pet, Adoption, Category, AdoptionPrice
from .serializers import (
    PetSerializer, AdoptionSerializer,
    CategorySerializer, AdoptionPriceSerializer
)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]


class PetViewSet(viewsets.ModelViewSet):
    queryset = Pet.objects.all()
    serializer_class = PetSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset =Pet.objects.all()
        user=self.request.user
        if user.is_authenticated:
            queryset=queryset.exclude(owner=user)
        return queryset
    
   

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def adopt(self, request, pk=None):
        """Custom action for adopting a pet"""
        pet = self.get_object()

        if not pet.is_available_for_adoption:
            return Response({'error': 'This pet has already been adopted.'}, status=400)

        adoption = Adoption.objects.create(
            pet=pet,
            adopter=request.user,
            is_confirmed=True,
            price_paid=pet.adoption_price,
        )

        pet.is_available_for_adoption = False
        pet.save()

        return Response(AdoptionSerializer(adoption).data, status=201)


class AdoptionViewSet(viewsets.ModelViewSet):
    queryset = Adoption.objects.all()
    serializer_class = AdoptionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class AdoptionPriceViewSet(viewsets.ModelViewSet):
    queryset = AdoptionPrice.objects.all()
    serializer_class = AdoptionPriceSerializer
    permission_classes = [permissions.IsAdminUser]

class MyPetViewSet(viewsets.ModelViewSet):
    serializer_class = PetSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Pet.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def perform_update(self, serializer):
        pet = self.get_object()
        if pet.owner != self.request.user:
            raise permissions.PermissionDenied("You can only update your own pets.")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.owner != self.request.user:
            raise permissions.PermissionDenied("You can only delete your own pets.")
        instance.delete()