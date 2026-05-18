from django.db import models
from django.contrib.auth.models import User


class PetAdoption(models.Model):
    # Basic info
    name = models.CharField(max_length=100)
    image = models.CharField(max_length=500)          # URL or path – increased length
    pet_type = models.CharField(max_length=100)       # e.g., Dog, Cat
    age_in_months = models.PositiveIntegerField(
        help_text="Age in months (e.g., 17 = 1 year 5 months)"
    )
    breed = models.CharField(max_length=100)
    gender = models.CharField(max_length=10)          # Male / Female
    description = models.TextField()

    # Health & status
    is_healthy = models.BooleanField(default=True)
    is_neutered = models.BooleanField(default=False)
    vaccination_status = models.BooleanField(default=False)
    adoption_status = models.BooleanField(default=False)   # False = available, True = adopted

    # Owner / submitter info
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pet_adoptions')
    user_nid = models.CharField(max_length=100)
    emergency_contact = models.CharField(max_length=20)
    street = models.CharField(max_length=100)
    area = models.CharField(max_length=100)
    city = models.CharField(max_length=100)

    #Approved
    is_approved = models.BooleanField(default=False)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.get_formatted_age()})"

    def get_formatted_age(self):
        """Returns age as string like '1 year 5 months'"""
        years = self.age_in_months // 12
        months = self.age_in_months % 12

        if years == 0:
            return f"{months} month{'s' if months != 1 else ''}"
        elif months == 0:
            return f"{years} year{'s' if years != 1 else ''}"
        else:
            return f"{years} year{'s' if years != 1 else ''} {months} month{'s' if months != 1 else ''}"

    # Optional: property to use as `obj.formatted_age`
    formatted_age = property(get_formatted_age)
