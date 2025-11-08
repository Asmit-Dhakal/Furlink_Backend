from rest_framework import serializers
from .models import Pet, Adoption, Category, AdoptionPrice


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class PetSerializer(serializers.ModelSerializer):
    owner_username = serializers.CharField(source='owner.username', read_only=True)
    adoption_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Pet
        fields = '__all__'
        read_only_fields = ['owner', 'is_available_for_adoption', 'adoption_price']


class AdoptionSerializer(serializers.ModelSerializer):
    pet_name = serializers.CharField(source='pet.name', read_only=True)
    adopter_username = serializers.CharField(source='adopter.username', read_only=True)

    class Meta:
        model = Adoption
        fields = '__all__'
        read_only_fields = ['price_paid', 'adopter', 'adoption_date']


class AdoptionPriceSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = AdoptionPrice
        fields = '__all__'