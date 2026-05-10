from django.db import models


class Tag(models.Model):
    """Pre-created tags that can be selected when creating a hospital."""
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Hospital(models.Model):
    # Basic Info
    image = models.CharField(max_length=500, blank=True, null=True)
    name = models.CharField(max_length=200)
    about = models.TextField()
    address = models.TextField()
    website = models.URLField(blank=True, null=True)

    # Opening Hours — stores a dict of day → {open, close}
    # e.g. {"saturday": {"open": "09:00", "close": "18:00"}, "sunday": {"open": "10:00", "close": "16:00"}, ...}
    opening_hours = models.JSONField(
        default=dict,
        help_text='e.g. {"saturday": {"open": "09:00", "close": "18:00"}, ...}'
    )

    # Contact Info
    phone_number = models.CharField(max_length=20)
    whatsapp_number = models.CharField(max_length=20, blank=True, null=True)

    # Tags (M2M — select one or more pre-existing tags)
    tags = models.ManyToManyField(Tag, blank=True, related_name='hospitals')

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Veterinarian(models.Model):
    """A vet belonging to a hospital. Created automatically from the hospital POST payload."""
    hospital = models.ForeignKey(
        Hospital, on_delete=models.CASCADE, related_name='veterinarians'
    )
    image = models.CharField(max_length=500, blank=True, null=True)
    name = models.CharField(max_length=100)
    specialization = models.CharField(max_length=200)
    experience = models.PositiveIntegerField(help_text="Years of experience")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'name']

    def __str__(self):
        return f"{self.name} - {self.specialization} ({self.experience} yrs)"
