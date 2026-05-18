from rest_framework import serializers
from .models import PetAdoption

class PetAdoptionSerializer(serializers.ModelSerializer):
    # Include the model property as a read-only field
    formatted_age = serializers.ReadOnlyField()

    class Meta:
        model = PetAdoption
        fields = [
            'id',
            'name',
            'image',
            'pet_type',
            'age_in_months',
            'formatted_age',          # computed from age_in_months
            'breed',
            'gender',
            'description',
            'is_healthy',
            'is_neutered',
            'vaccination_status',
            'adoption_status',
            'user',
            'user_nid',
            'emergency_contact',
            'street',
            'area',
            'city',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'user']  # user often set automatically