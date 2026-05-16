# serializers.py
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.models import User
import re

# =============== REGISTRATION SERIALIZERS ===============

class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    username = serializers.CharField(max_length=150)
    phone = serializers.CharField(max_length=20)
    password = serializers.CharField(max_length=128, write_only=True)
    confirm_password = serializers.CharField(max_length=128, write_only=True)
    first_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    
    def validate_phone(self, value):
        phone_clean = re.sub(r'\D', '', value)
        if len(phone_clean) < 10 or len(phone_clean) > 15:
            raise serializers.ValidationError("Phone number must be between 10-15 digits")
        return phone_clean
    
    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({
                "confirm_password": "Passwords do not match"
            })
        if len(data['password']) < 8:
            raise serializers.ValidationError({
                "password": "Password must be at least 8 characters"
            })
        return data


class OTPVerifySerializer(serializers.Serializer):
    request_id = serializers.UUIDField()
    otp = serializers.CharField(max_length=6, min_length=6)
    
    def validate_otp(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("OTP must contain only digits")
        return value


class GoogleAuthSerializer(serializers.Serializer):
    google_token = serializers.CharField(required=True)
    email = serializers.EmailField(required=False)
    username = serializers.CharField(max_length=150, required=False)
    first_name = serializers.CharField(max_length=150, required=False, allow_blank=True, default='')
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True, default='')
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True, default='')
    google_id = serializers.CharField(required=False, allow_blank=True, default='')

# =============== LOGIN SERIALIZERS ===============

class EmailLoginSerializer(serializers.Serializer):
    """Login with email and password"""
    email = serializers.EmailField()
    password = serializers.CharField(max_length=128)


class PhoneLoginSerializer(serializers.Serializer):
    """Login with phone and password"""
    phone = serializers.CharField(max_length=20)
    password = serializers.CharField(max_length=128)
    
    def validate_phone(self, value):
        phone_clean = re.sub(r'\D', '', value)
        if len(phone_clean) < 10 or len(phone_clean) > 15:
            raise serializers.ValidationError("Phone number must be between 10-15 digits")
        return phone_clean


class GoogleLoginSerializer(serializers.Serializer):
    """Login with Google OAuth"""
    google_token = serializers.CharField(required=True)
    email = serializers.EmailField()

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims
        token['email'] = user.email
        token['username'] = user.username
        token['first_name'] = user.first_name
        token['last_name'] = user.last_name
        
        try:
            user_model = user.userinfo
            token['phone'] = user_model.phone
            token['is_phone_verified'] = user_model.is_phone_verified
        except Exception:
            token['phone'] = None
            token['is_phone_verified'] = False
            
        return token