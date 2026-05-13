from rest_framework import serializers
from .models import Tag, Hospital, Veterinarian, Appointment


# =============== TAG SERIALIZER ===============

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']


# =============== VETERINARIAN SERIALIZER ===============

class VeterinarianSerializer(serializers.ModelSerializer):
    class Meta:
        model = Veterinarian
        fields = ['id', 'image', 'name', 'specialization', 'experience', 'order']


# =============== HOSPITAL SERIALIZERS ===============

class HospitalListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing hospitals."""
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = Hospital
        fields = [
            'id', 'image', 'name', 'about', 'address', 'website',
            'opening_hours', 'phone_number', 'whatsapp_number',
            'tags', 'created_at', 'updated_at',
        ]


class HospitalDetailSerializer(serializers.ModelSerializer):
    """Full serializer — includes nested veterinarians."""
    tags = TagSerializer(many=True, read_only=True)
    veterinarians = VeterinarianSerializer(many=True, read_only=True)

    class Meta:
        model = Hospital
        fields = [
            'id', 'image', 'name', 'about', 'address', 'website',
            'opening_hours', 'phone_number', 'whatsapp_number',
            'tags', 'veterinarians', 'created_at', 'updated_at',
        ]


class HospitalCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Accepts the full hospital payload including:
      - tag_ids: list of existing Tag PKs  (e.g. [1, 3, 5])
      - veterinarians: list of vet objects  (created / replaced on save)
    """
    tag_ids = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=False
    )
    veterinarians = VeterinarianSerializer(many=True, required=False, write_only=True)

    class Meta:
        model = Hospital
        fields = [
            'id', 'image', 'name', 'about', 'address', 'website',
            'opening_hours', 'phone_number', 'whatsapp_number',
            'tag_ids', 'veterinarians', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    # ---------- validation ----------

    def validate_tag_ids(self, value):
        """Make sure every supplied tag ID actually exists."""
        existing = set(Tag.objects.filter(id__in=value).values_list('id', flat=True))
        missing = set(value) - existing
        if missing:
            raise serializers.ValidationError(
                f"Tags with ids {missing} do not exist."
            )
        return value

    VALID_DAYS = {
        'saturday', 'sunday', 'monday', 'tuesday',
        'wednesday', 'thursday', 'friday',
    }

    def validate_opening_hours(self, value):
        """Ensure opening_hours is a dict of day → {open, close} and normalize keys."""
        if not isinstance(value, dict):
            raise serializers.ValidationError("opening_hours must be a JSON object.")

        normalized_value = {}
        for day, hours in value.items():
            day_lower = day.lower()
            if day_lower not in self.VALID_DAYS:
                raise serializers.ValidationError(f"Invalid day: {day}")
            if not isinstance(hours, dict) or 'open' not in hours or 'close' not in hours:
                raise serializers.ValidationError(
                    f"Each day must have 'open' and 'close' keys. Problem with: {day}"
                )
            normalized_value[day_lower] = hours
        return normalized_value

    # ---------- create / update ----------

    def create(self, validated_data):
        tag_ids = validated_data.pop('tag_ids', [])
        vets_data = validated_data.pop('veterinarians', [])

        hospital = Hospital.objects.create(**validated_data)

        # Set M2M tags
        if tag_ids:
            hospital.tags.set(tag_ids)

        # Bulk-create veterinarians
        if vets_data:
            Veterinarian.objects.bulk_create([
                Veterinarian(hospital=hospital, **vet) for vet in vets_data
            ])

        return hospital

    def update(self, instance, validated_data):
        tag_ids = validated_data.pop('tag_ids', None)
        vets_data = validated_data.pop('veterinarians', None)

        # Update scalar fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update tags if provided
        if tag_ids is not None:
            instance.tags.set(tag_ids)

        # Replace veterinarians if provided
        if vets_data is not None:
            instance.veterinarians.all().delete()
            Veterinarian.objects.bulk_create([
                Veterinarian(hospital=instance, **vet) for vet in vets_data
            ])

        return instance

    def to_representation(self, instance):
        """Return the full detail representation after create/update."""
        return HospitalDetailSerializer(instance).data

from django.contrib.auth.models import User
from .models import Appointment, Hospital

class UserSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(source='userinfo.phone', read_only=True)
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'phone']

class HospitalInAppSerializer(serializers.ModelSerializer):   # must be defined
    class Meta:
        model = Hospital
        fields = ['id', 'image', 'name', 'address']

class AppointmentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ['id', 'hospital']

class AppointmentDetailSerializer(serializers.ModelSerializer):
    hospital = HospitalInAppSerializer(read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = Appointment
        fields = ['id', 'hospital', 'user']