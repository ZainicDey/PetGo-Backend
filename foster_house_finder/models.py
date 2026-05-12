from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Tag(models.Model):
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
    # Using ManyToManyField instead of ForeignKey because you mentioned
    # "select one of or multiple of them". A ForeignKey only allows selecting one.
    tags = models.ManyToManyField(Tag, blank=True, related_name='foster_houses')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

