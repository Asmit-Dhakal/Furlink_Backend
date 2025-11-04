from rest_framework import serializers
from .models import PetImage

class PetImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PetImage
        fields = ['id', 'image', 'breed', 'description', 'created_at']
