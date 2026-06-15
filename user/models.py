from django.db import models
from django.contrib.auth.models import User
import uuid
from django.utils import timezone

User._meta.get_field('email')._unique = True

class UserModel(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userinfo')
    phone = models.CharField(max_length=20, unique=True)
    is_phone_verified = models.BooleanField(default=False)
    
    def __str__(self):
        return self.user.username

class TemporaryUser(models.Model):
    """Temporary storage for users awaiting OTP verification"""
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    phone = models.CharField(max_length=20)
    password = models.CharField(max_length=128)  # Hashed password
    auth_method = models.CharField(max_length=20)  # 'sms_otp' or 'google'
    otp = models.CharField(max_length=6)
    otp_created_at = models.DateTimeField(auto_now_add=True)
    request_id = models.UUIDField(default=uuid.uuid4, unique=True)
    is_verified = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.username} - {self.email}"
    
    def is_otp_expired(self):
        """OTP expires after 10 minutes"""
        expiry_time = self.otp_created_at + timezone.timedelta(minutes=10)
        return timezone.now() > expiry_time

class UserAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    street = models.CharField(max_length=100)
    area = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.user.username} - {self.street} {self.area} {self.city} {self.zip_code}"