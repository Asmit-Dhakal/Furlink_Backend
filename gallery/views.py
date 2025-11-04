
from rest_framework import viewsets
from .models import PetImage
from .serializers import PetImageSerializer

class PetImageViewSet(viewsets.ModelViewSet):
	queryset = PetImage.objects.all()
	serializer_class = PetImageSerializer
