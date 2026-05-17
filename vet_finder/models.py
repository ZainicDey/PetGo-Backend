from django.db import models, transaction
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class HospitalTag(models.Model):
    """Pre-created tags that can be selected when creating a hospital."""
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class HospitalServices(models.Model):
    name = models.CharField(max_length=50, unique=True)
    def __str__(self):
        return self.name

class Hospital(models.Model):
    # Basic Info
    image = models.CharField(max_length=500, blank=True, null=True)
    name = models.CharField(max_length=200)
    about = models.TextField()
    street = models.TextField()
    area = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
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

    # Tags (M2M — select one or more pre-existing tags)
    tags = models.ManyToManyField(HospitalTag, blank=True, related_name='hospitals')

    # Services (M2M — select one or more pre-existing services)
    services = models.ManyToManyField(HospitalServices, blank=True, related_name='hospitals')
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    review_count = models.IntegerField(default=0)
    review_sum = models.IntegerField(default=0)
    average_rating = models.DecimalField(max_digits=3, decimal_places=1, default=0)
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

class Appointment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vet_appointments', null=True, blank=True)
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='vet_appointments', null=True, blank=True)

    def __str__(self):
        return self.user.username


class HospitalReview(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vet_reviews', null=True, blank=True)
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='vet_reviews', null=True, blank=True)
    review = models.TextField()
    rating = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(5)])

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # optional: a user can only review a hospital once
        unique_together = ['user', 'hospital']


    def save(self, *args, **kwargs):
        is_new = self.pk is None

        with transaction.atomic():
            hospital = Hospital.objects.select_for_update().get(pk=self.hospital_id)

            if not is_new:
                old = HospitalReview.objects.get(pk=self.pk)
                hospital.review_sum -= old.rating  # remove old rating first

            super().save(*args, **kwargs)

            if is_new:
                hospital.review_count += 1

            hospital.review_sum += self.rating
            hospital.average_rating = round(hospital.review_sum / hospital.review_count, 1)
            hospital.save(update_fields=['review_count', 'review_sum', 'average_rating'])


    def delete(self, *args, **kwargs):
        with transaction.atomic():
            hospital = Hospital.objects.select_for_update().get(pk=self.hospital_id)
            hospital.review_sum -= self.rating
            hospital.review_count -= 1
            hospital.average_rating = (
                round(hospital.review_sum / hospital.review_count, 1)
                if hospital.review_count > 0 else 0
            )
            super().delete(*args, **kwargs)
            hospital.save(update_fields=['review_count', 'review_sum', 'average_rating'])

class HospitalReviewReply(models.Model):
    review = models.ForeignKey(HospitalReview, on_delete=models.CASCADE, related_name='vet_review_replies', null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vet_review_replies', null=True, blank=True)
    reply = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.reply