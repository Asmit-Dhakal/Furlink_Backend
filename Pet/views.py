from django.shortcuts import render
from rest_framework import viewsets, permissions
from .models import Pet
from .serializers import PetSerializer

# Create your views here.

class PetViewSet(viewsets.ModelViewSet):
    queryset = Pet.objects.all()
    serializer_class = PetSerializer
