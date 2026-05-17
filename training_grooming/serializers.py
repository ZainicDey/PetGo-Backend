from rest_framework import serializers
from .models import TrainingGroomingTag, TrainingGrooming, TrainingGroomingServices, TrainingGroomingReview, TrainingGroomingReviewReply

# =============== TAG SERIALIZER ===============

class TrainingGroomingTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingGroomingTag
        fields = ['id', 'name']

class TrainingGroomingServicesSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingGroomingServices
        fields = ['id', 'name']
        
# =============== HOSPITAL SERIALIZERS ===============

class TrainingGroomingSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing hospitals."""
    tags = TrainingGroomingTagSerializer(many=True, read_only=True)
    services = TrainingGroomingServicesSerializer(many=True, read_only=True)

    class Meta:
        model = TrainingGrooming
        fields = [
            'id', 'image', 'name', 'about', 'street', 'area', 'city','website',
            'opening_hours', 'phone_number', 'whatsapp_number',
            'tags', 'services', 'created_at', 'updated_at',
        ]


class TrainingGroomingDetailSerializer(serializers.ModelSerializer):
    """Full serializer"""
    tags = TrainingGroomingTagSerializer(many=True, read_only=True)
    services = TrainingGroomingServicesSerializer(many=True, read_only=True)

    class Meta:
        model = TrainingGrooming
        fields = [
            'id', 'image', 'name', 'about','street', 'area', 'city', 'website',
            'opening_hours', 'phone_number', 'whatsapp_number',
            'tags', 'services', 'created_at', 'updated_at',
        ]


class TrainingGroomingCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Accepts the full hospital payload including:
      - tag_ids: list of existing Tag PKs  (e.g. [1, 3, 5])
    """
    tag_ids = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=False
    )
    service_ids = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=False
    )

    class Meta:
        model = TrainingGrooming
        fields = [
            'id', 'image', 'name', 'about','street', 'area', 'city', 'website',
            'opening_hours', 'phone_number', 'whatsapp_number',
            'tag_ids', 'service_ids', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    # ---------- validation ----------

    def validate_tag_ids(self, value):
        """Make sure every supplied tag ID actually exists."""
        existing = set(TrainingGroomingTag.objects.filter(id__in=value).values_list('id', flat=True))
        missing = set(value) - existing
        if missing:
            raise serializers.ValidationError(
                f"Tags with ids {missing} do not exist."
            )
        return value

    def validate_service_ids(self, value):
        """Make sure every supplied service ID actually exists."""
        existing = set(TrainingGroomingServices.objects.filter(id__in=value).values_list('id', flat=True))
        missing = set(value) - existing
        if missing:
            raise serializers.ValidationError(
                f"Services with ids {missing} do not exist."
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
        service_ids = validated_data.pop('service_ids', [])

        training_grooming = TrainingGrooming.objects.create(**validated_data)

        # Set M2M tags
        if tag_ids:
            training_grooming.tags.set(tag_ids)
        
        # Set M2M services
        if service_ids:
            training_grooming.services.set(service_ids)

        return training_grooming

    def update(self, instance, validated_data):
        tag_ids = validated_data.pop('tag_ids', None)
        service_ids = validated_data.pop('service_ids', None)

        # Update scalar fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update tags if provided
        if tag_ids is not None:
            instance.tags.set(tag_ids)
        
        # Update services if provided
        if service_ids is not None:
            instance.services.set(service_ids)

        return instance

    def to_representation(self, instance):
        """Return the full detail representation after create/update."""
        return TrainingGroomingDetailSerializer(instance).data

from django.contrib.auth.models import User
from .models import Appointment, TrainingGrooming

class UserSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(source='userinfo.phone', read_only=True)
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'phone']

class TrainingGroomingInAppSerializer(serializers.ModelSerializer):   # must be defined
    class Meta:
        model = TrainingGrooming
        fields = ['id', 'image', 'name', 'street', 'area', 'city']

class AppointmentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ['id', 'training_grooming']

class AppointmentDetailSerializer(serializers.ModelSerializer):
    training_grooming = TrainingGroomingInAppSerializer(read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = Appointment
        fields = ['id', 'training_grooming', 'user']

class TrainingGroomingReviewReplySerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = TrainingGroomingReviewReply
        fields = ['id', 'review', 'user', 'reply', 'created_at', 'updated_at']
        read_only_fields = ['user', 'created_at', 'updated_at']

class TrainingGroomingReviewSerializer(serializers.ModelSerializer):
    replies = TrainingGroomingReviewReplySerializer(many=True, read_only=True, source='training_grooming_review_replies')
    user = UserSerializer(read_only=True)
    class Meta:
        model = TrainingGroomingReview
        fields = ['id', 'training_grooming', 'user', 'review', 'rating', 'created_at', 'updated_at', 'replies']
        read_only_fields = ['user','replies', 'created_at', 'updated_at']
