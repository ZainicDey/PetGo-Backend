from django.db import models, transaction
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
    street = models.TextField()
    area = models.TextField()
    city = models.TextField()
    website = models.CharField(max_length=200, blank=True, null=True)
    
    # Reviews
    review_count = models.IntegerField(default=0)
    review_sum = models.IntegerField(default=0)
    average_rating = models.DecimalField(max_digits=3, decimal_places=1, default=0)
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
        # optional: a user can only review a house once
        unique_together = ['user', 'house']


    def save(self, *args, **kwargs):
        is_new = self.pk is None

        with transaction.atomic():
            house = House.objects.select_for_update().get(pk=self.house_id)

            if not is_new:
                old = HouseReview.objects.get(pk=self.pk)
                house.review_sum -= old.rating  # remove old rating first

            super().save(*args, **kwargs)

            if is_new:
                house.review_count += 1

            house.review_sum += self.rating
            house.average_rating = round(house.review_sum / house.review_count, 1)
            house.save(update_fields=['review_count', 'review_sum', 'average_rating'])


    def delete(self, *args, **kwargs):
        with transaction.atomic():
            house = House.objects.select_for_update().get(pk=self.house_id)
            house.review_sum -= self.rating
            house.review_count -= 1
            house.average_rating = (
                round(house.review_sum / house.review_count, 1)
                if house.review_count > 0 else 0
            )
            super().delete(*args, **kwargs)
            house.save(update_fields=['review_count', 'review_sum', 'average_rating'])

class HouseReviewReply(models.Model):
    review = models.ForeignKey(HouseReview, on_delete=models.CASCADE, related_name='house_review_replies', null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='house_review_replies', null=True, blank=True)
    reply = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.reply