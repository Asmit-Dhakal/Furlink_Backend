from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Pet, Adoption, Category, AdoptionPrice
from .serializers import (
    PetSerializer, AdoptionSerializer, CategorySerializer, AdoptionPriceSerializer
)


class PetViewSet(viewsets.ModelViewSet):
    """CRUD for Pet. Uses soft-delete by default (Pet.objects hides deleted items).
    Provides a `restore` action to undelete a pet (owner or staff only).
    """
    permission_classes = [permissions.IsAuthenticated]
    queryset = Pet.objects.all()
    serializer_class = PetSerializer

    @action(detail=True, methods=['post'], url_path='restore')
    def restore(self, request, pk=None):
        """Restore a soft-deleted pet. Allowed for the pet owner or staff."""
        # allow restoring only if the pet exists in all_objects and is deleted
        try:
            pet = Pet.all_objects.get(pk=pk)
        except Pet.DoesNotExist:
            return Response({'detail': 'Pet not found.'}, status=status.HTTP_404_NOT_FOUND)

        # check if deleted
        if not pet.is_deleted:
            return Response({'detail': 'Pet is not deleted.'}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        # only owner or staff can restore
        if not (user.is_staff or pet.owner_id == getattr(user, 'id', None)):
            return Response({'detail': 'Not permitted to restore this pet.'}, status=status.HTTP_403_FORBIDDEN)

        pet.restore()
        serializer = self.get_serializer(pet)
        return Response(serializer.data)


class AdoptionViewSet(viewsets.ModelViewSet):
    """Manage adoptions. Only authenticated users can create/update."""
    permission_classes = [permissions.IsAuthenticated]
    queryset = Adoption.objects.all()
    serializer_class = AdoptionSerializer


class CategoryViewSet(viewsets.ModelViewSet):
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
