from rest_framework import viewsets, permissions
from .models import Pet, Adoption
from .serializers import PetSerializer, AdoptionSerializer


class PetViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Pet.objects.all()
    serializer_class = PetSerializer


class AdoptionViewSet(viewsets.ModelViewSet):
    """Manage adoptions. Only authenticated users can create/update."""
    permission_classes = [permissions.IsAuthenticated]
    queryset = Adoption.objects.all()
    serializer_class = AdoptionSerializer
