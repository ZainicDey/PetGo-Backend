from rest_framework import serializers
from .models import PetAdoption
from django.utils import timezone
from datetime import timedelta

class PetAdoptionListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing pet adoptions."""
    formatted_age = serializers.ReadOnlyField()
    created_at_display = serializers.SerializerMethodField()

    class Meta:
        model = PetAdoption
        fields = [
            'id',
            'name',
            'image',
            'pet_type',
            'age_in_months',
            'formatted_age',
            'breed',
            'gender',
            'adoption_status',
            'street',
            'area',
            'city',
            'created_at_display',
        ]

    def get_created_at_display(self, obj):
        """Convert created_at to relative time format (e.g., '2 days ago')."""
        now = timezone.now()
        diff = now - obj.created_at
        
        # Seconds
        if diff < timedelta(minutes=1):
            return "just now"
        
        # Minutes
        minutes = diff.total_seconds() / 60
        if minutes < 60:
            return f"{int(minutes)} minute{'s' if int(minutes) != 1 else ''} ago"
        
        # Hours
        hours = minutes / 60
        if hours < 24:
            return f"{int(hours)} hour{'s' if int(hours) != 1 else ''} ago"
        
        # Days
        days = diff.days
        if days == 1:
            return "1 day ago"
        if days < 7:
            return f"{days} days ago"
        
        # Weeks
        weeks = days // 7
        if weeks == 1:
            return "1 week ago"
        if weeks < 4:
            return f"{weeks} weeks ago"
        
        # Months (approximate)
        months = days // 30
        if months == 1:
            return "1 month ago"
        if months < 12:
            return f"{months} months ago"
        
        # Years
        years = days // 365
        if years == 1:
            return "1 year ago"
        return f"{years} years ago"


class PetAdoptionDetailSerializer(serializers.ModelSerializer):
    """Full serializer — includes detailed information."""
    formatted_age = serializers.ReadOnlyField()
    created_at_display = serializers.SerializerMethodField()
    updated_at_display = serializers.SerializerMethodField()

    class Meta:
        model = PetAdoption
        fields = [
            'id',
            'name',
            'image',
            'pet_type',
            'age_in_months',
            'formatted_age',
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
            'created_at_display',
            'updated_at',
            'updated_at_display',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'user']

    def get_created_at_display(self, obj):
        """Convert created_at to relative time format (e.g., '2 days ago')."""
        now = timezone.now()
        diff = now - obj.created_at
        
        # Seconds
        if diff < timedelta(minutes=1):
            return "just now"
        
        # Minutes
        minutes = diff.total_seconds() / 60
        if minutes < 60:
            return f"{int(minutes)} minute{'s' if int(minutes) != 1 else ''} ago"
        
        # Hours
        hours = minutes / 60
        if hours < 24:
            return f"{int(hours)} hour{'s' if int(hours) != 1 else ''} ago"
        
        # Days
        days = diff.days
        if days == 1:
            return "1 day ago"
        if days < 7:
            return f"{days} days ago"
        
        # Weeks
        weeks = days // 7
        if weeks == 1:
            return "1 week ago"
        if weeks < 4:
            return f"{weeks} weeks ago"
        
        # Months (approximate)
        months = days // 30
        if months == 1:
            return "1 month ago"
        if months < 12:
            return f"{months} months ago"
        
        # Years
        years = days // 365
        if years == 1:
            return "1 year ago"
        return f"{years} years ago"

    def get_updated_at_display(self, obj):
        """Convert updated_at to relative time format."""
        now = timezone.now()
        diff = now - obj.updated_at
        
        # Seconds
        if diff < timedelta(minutes=1):
            return "just now"
        
        # Minutes
        minutes = diff.total_seconds() / 60
        if minutes < 60:
            return f"{int(minutes)} minute{'s' if int(minutes) != 1 else ''} ago"
        
        # Hours
        hours = minutes / 60
        if hours < 24:
            return f"{int(hours)} hour{'s' if int(hours) != 1 else ''} ago"
        
        # Days
        days = diff.days
        if days == 1:
            return "1 day ago"
        if days < 7:
            return f"{days} days ago"
        
        # Weeks
        weeks = days // 7
        if weeks == 1:
            return "1 week ago"
        if weeks < 4:
            return f"{weeks} weeks ago"
        
        # Months (approximate)
        months = days // 30
        if months == 1:
            return "1 month ago"
        if months < 12:
            return f"{months} months ago"
        
        # Years
        years = days // 365
        if years == 1:
            return "1 year ago"
        return f"{years} years ago"