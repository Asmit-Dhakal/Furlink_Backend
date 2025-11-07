from rest_framework import serializers
from .models import Pet, Adoption, Category, AdoptionPrice


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description']


class AdoptionPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdoptionPrice
        fields = [
            'id', 'category', 'adopter', 'price', 'currency', 'is_active', 'effective_from', 'effective_to',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class PetSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), source='category', write_only=True, allow_null=True, required=False)

    class Meta:
        model = Pet
        fields = [
            'id', 'owner', 'name', 'species', 'breed', 'category', 'category_id', 'age', 'gender', 'color', 'weight',
            'health_issues', 'vaccination_status', 'photo', 'description'
        ]
        read_only_fields = ['owner']

    def create(self, validated_data):
        # set owner from request
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        if user and not validated_data.get('owner'):
            validated_data['owner'] = user
        return super().create(validated_data)



class AdoptionSerializer(serializers.ModelSerializer):
    adopter = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Adoption
        fields = ['id', 'pet', 'adopter', 'adoption_date', 'remarks', 'is_adopted']
        read_only_fields = ['adopter', 'adoption_date']

    def validate(self, attrs):
        pet = attrs.get('pet')
        # OneToOne relation; check existence safely
        from .models import Adoption as AdoptionModel
        if pet and AdoptionModel.objects.filter(pet=pet).exists():
            raise serializers.ValidationError('This pet already has an adoption record.')
        return attrs

    def create(self, validated_data):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        validated_data['adopter'] = user
        # mark as adopted by default when creating adoption
        validated_data['is_adopted'] = True
        return super().create(validated_data)


