from rest_framework import serializers
from .models import PetAdoption

class PetAdoptionSerializer(serializers.ModelSerializer):
    # This will output the readable age string instead of months
    age = serializers.CharField(source='formatted_age', read_only=True)

    class Meta:
        model = PetAdoption
        fields = [
            'id', 'name', 'image', 'pet_type', 'age',          # 'age' is the formatted string
            'breed', 'gender', 'description', 'is_healthy',
            'is_neutered', 'vaccination_status', 'adoption_status',
            'user', 'user_nid', 'emergency_contact',
            'street', 'area', 'city', 'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'created_at', 'updated_at']

    # Optional: If you want to accept months during creation
    def create(self, validated_data):
        # The client should send 'age_in_months' in the request,
        # but we removed it from fields. To accept it, add it back temporarily.
        # Better: use a write-only field.
        pass