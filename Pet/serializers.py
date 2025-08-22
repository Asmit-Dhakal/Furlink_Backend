from rest_framework import serializers
from .models import Pet
from authuser.models import User

class PetSerializer(serializers.ModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    keeper = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), allow_null=True, required=False)

    class Meta:
        model = Pet
        fields = [
            'id',
            'owner',
            'keeper',
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
            'admission_date',
            'status',
            'description',
        ]
        read_only_fields = ['admission_date']

