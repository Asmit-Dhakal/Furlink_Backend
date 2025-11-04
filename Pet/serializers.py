from rest_framework import serializers
from .models import Pet, Adoption
# owner/adopter are set from request.user in serializers; no direct User import needed here


class PetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pet
        fields = [
            'id',
            'owner',
            'name',
            'species',
            'breed',
            'age',
            'gender',
            'color',
            'weight',
            'health_issues',
            'vaccination_status',
            'photo',
            'description',
        ]
        read_only_fields = ['owner']

    def create(self, validated_data):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
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
        if hasattr(pet, 'adoptions'):
            raise serializers.ValidationError('This pet already has an adoption record.')
        return attrs

    def create(self, validated_data):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        validated_data['adopter'] = user
        # mark as adopted by default when creating adoption
        validated_data['is_adopted'] = True
        return super().create(validated_data)

