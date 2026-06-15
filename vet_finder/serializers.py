from rest_framework import serializers
from .models import HospitalTag, Hospital, Veterinarian, Appointment, HospitalReview, HospitalReviewReply, HospitalServices
from django.utils import timezone
import datetime

# =============== TAG SERIALIZER ===============

class HospitalTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = HospitalTag
        fields = ['id', 'name']

# =============== HOSPITAL SERVICES SERIALIZER ===============
class HospitalServicesSerializer(serializers.ModelSerializer):
    class Meta:
        model = HospitalServices
        fields = ['id', 'name']

# =============== VETERINARIAN SERIALIZER ===============

class VeterinarianSerializer(serializers.ModelSerializer):
    class Meta:
        model = Veterinarian
        fields = ['id', 'image', 'name', 'specialization', 'experience', 'order']


# =============== HOSPITAL SERIALIZERS ===============

class HospitalListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing hospitals."""
    tag_names = serializers.SerializerMethodField()
    service_names = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    class Meta:
        model = Hospital
        fields = [
            'id', 'image', 'name', 'street', 'area', 'city',
            'phone_number', 'whatsapp_number', 'average_rating', 'tag_names', 
            'service_names', 'status'
        ]

    def get_tag_names(self, obj):
        return [tag.name for tag in obj.tags.all()]

    def get_service_names(self, obj):
        return [service.name for service in obj.services.all()]

    def get_status(self, obj):
        # Your existing status logic
        now = timezone.localtime(timezone.now())
        current_day = now.strftime('%A').lower()
        current_time = now.time()
        hours_today = obj.opening_hours.get(current_day)
        
        if not hours_today:
            return "Closed"

        try:
            open_time = datetime.datetime.strptime(hours_today.get('open'), "%H:%M").time()
            close_time = datetime.datetime.strptime(hours_today.get('close'), "%H:%M").time()
            
            if open_time <= close_time:
                return "Open" if open_time <= current_time <= close_time else "Closed"
            else:
                return "Open" if current_time >= open_time or current_time <= close_time else "Closed"
        except (ValueError, TypeError):
            return "Closed"

    def get_status(self, obj):
        # Gets the time in 'Asia/Dhaka' regardless of server location
        now = timezone.localtime(timezone.now())
        
        current_day = now.strftime('%A').lower()
        current_time = now.time()

        hours_today = obj.opening_hours.get(current_day)
        
        # Return "Closed" strings instead of False
        if not hours_today:
            return "Closed" 

        try:
            open_str = hours_today.get('open')
            close_str = hours_today.get('close')
            
            if not open_str or not close_str:
                return "Closed"

            open_time = datetime.datetime.strptime(open_str, "%H:%M").time()
            close_time = datetime.datetime.strptime(close_str, "%H:%M").time()

            # Determine boolean first
            if open_time <= close_time:
                is_currently_open = open_time <= current_time <= close_time
            else:
                is_currently_open = current_time >= open_time or current_time <= close_time

            # Return the exact string based on the boolean
            return "Open" if is_currently_open else "Closed"

        except (ValueError, TypeError):
            # Fallback for bad data
            return "Closed"

class HospitalDetailSerializer(serializers.ModelSerializer):
    """Full serializer — includes nested veterinarians."""
    tag_names = serializers.SerializerMethodField()
    service_names = serializers.SerializerMethodField()
    veterinarians = VeterinarianSerializer(many=True, read_only=True)

    class Meta:
        model = Hospital
        fields = [
            'id', 'image', 'name', 'about', 'street', 'area', 'city', 'website',
            'opening_hours', 'phone_number', 'whatsapp_number', 'average_rating',
            'tag_names', 'service_names', 'veterinarians', 'created_at', 'updated_at',
        ]

    def get_tag_names(self, obj):
        return [tag.name for tag in obj.tags.all()]

    def get_service_names(self, obj):
        return [service.name for service in obj.services.all()]

class HospitalCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Accepts the full hospital payload including:
      - tag_ids: list of existing Tag PKs  (e.g. [1, 3, 5])
      - veterinarians: list of vet objects  (created / replaced on save)
    """
    tag_ids = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=False
    )
    services_ids = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=False
    )
    veterinarians = VeterinarianSerializer(many=True, required=False, write_only=True)

    class Meta:
        model = Hospital
        fields = [
            'id', 'image', 'name', 'about', 'street', 'area', 'city', 'website',
            'opening_hours', 'phone_number', 'whatsapp_number',
            'tag_ids', 'services_ids', 'veterinarians', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'review_count', 'review_sum', 'average_rating']

    # ---------- validation ----------

    def validate_tag_ids(self, value):
        """Make sure every supplied tag ID actually exists."""
        existing = set(HospitalTag.objects.filter(id__in=value).values_list('id', flat=True))
        missing = set(value) - existing
        if missing:
            raise serializers.ValidationError(
                f"Tags with ids {missing} do not exist."
            )
        return value
    def validate_services_ids(self, value):
        """Ensure service IDs exist (if supplied)."""
        existing = set(HospitalServices.objects.filter(id__in=value).values_list('id', flat=True))
        missing = set(value) - existing
        if missing:
            raise serializers.ValidationError(f"Services with IDs {missing} do not exist.")
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
        services_ids = validated_data.pop('services_ids', [])
        vets_data = validated_data.pop('veterinarians', [])

        hospital = Hospital.objects.create(**validated_data)

        # Set M2M tags
        if tag_ids:
            hospital.tags.set(tag_ids)
        # Set M2M services
        if services_ids:
            hospital.services.set(services_ids)

        # Bulk-create veterinarians
        if vets_data:
            Veterinarian.objects.bulk_create([
                Veterinarian(hospital=hospital, **vet) for vet in vets_data
            ])

        return hospital

    def update(self, instance, validated_data):
        tag_ids = validated_data.pop('tag_ids', None)
        services_ids = validated_data.pop('services_ids', None)
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
        
        # Update services if provided
        if services_ids is not None:
            instance.services.set(services_ids)
    
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
        fields = ['id', 'image', 'name', 'street', 'area', 'city']

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

class HospitalReviewReplySerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = HospitalReviewReply
        fields = ['id', 'review', 'user', 'reply', 'created_at', 'updated_at']
        read_only_fields = ['user', 'created_at', 'updated_at']

class HospitalReviewSerializer(serializers.ModelSerializer):
    replies = HospitalReviewReplySerializer(many=True, read_only=True, source='vet_review_replies')
    user = UserSerializer(read_only=True)
    class Meta:
        model = HospitalReview
        fields = ['id', 'hospital', 'user', 'review', 'rating', 'created_at', 'updated_at', 'replies']
        read_only_fields = ['user','replies', 'created_at', 'updated_at']
