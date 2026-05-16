from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class FosterHouseTag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return self.name
    
class FosterHouseServices(models.Model):
    name = models.CharField(max_length=50, unique=True)
    def __str__(self):
        return self.name

class House(models.Model):
    # Basic Info
    image = models.CharField(max_length=500, blank=True, null=True)
    name = models.CharField(max_length=200)
    about = models.TextField()
    address = models.TextField()
    website = models.URLField(blank=True, null=True)
    
    # Opening Hours — stores a dict of day → {open, close}
    opening_hours = models.JSONField(
        default=dict,
        blank=True,
        help_text='e.g. {"saturday": {"open": "09:00", "close": "18:00"}, ...}'
    )


    # Contact Info
    phone_number = models.CharField(max_length=20)
    whatsapp_number = models.CharField(max_length=20, blank=True, null=True)
    # Tags
    tags = models.ManyToManyField(FosterHouseTag, blank=True, related_name='foster_houses')
    # Services
    services = models.ManyToManyField(FosterHouseServices, blank=True, related_name='foster_houses')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

from django.contrib.auth.models import User

class Appointment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='foster_house_appointments')
    house = models.ForeignKey(House, on_delete=models.CASCADE, null=True, blank=True, related_name='foster_house_appointments')

    def __str__(self):
        return self.user.username

class HouseReview(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='house_reviews', null=True, blank=True)
    house = models.ForeignKey(House, on_delete=models.CASCADE, related_name='house_reviews', null=True, blank=True)
    review = models.TextField()
    rating = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(5)])
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # optional: a user can only review a hospital once
        unique_together = ['user', 'house']

    def __str__(self):
        return self.user.username