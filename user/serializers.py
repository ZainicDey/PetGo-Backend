# serializers.py
from rest_framework import serializers
import re

class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    username = serializers.CharField(max_length=150)
    phone = serializers.CharField(max_length=20)
    password = serializers.CharField(max_length=128, write_only=True)
    confirm_password = serializers.CharField(max_length=128, write_only=True)
    first_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    
    def validate_phone(self, value):
        """Validate phone number format"""
        # Remove any non-digit characters
        phone_clean = re.sub(r'\D', '', value)
        
        # Basic validation - adjust based on your country format
        if len(phone_clean) < 10 or len(phone_clean) > 15:
            raise serializers.ValidationError("Phone number must be between 10-15 digits")
        
        return phone_clean
    
    def validate(self, data):
        """Cross-field validation"""
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({
                "confirm_password": "Passwords do not match"
            })
        return data


class OTPVerifySerializer(serializers.Serializer):
    request_id = serializers.UUIDField()
    otp = serializers.CharField(max_length=6, min_length=6)
    
    def validate_otp(self, value):
        """Validate OTP is 6 digits"""
        if not value.isdigit():
            raise serializers.ValidationError("OTP must contain only digits")
        return value


class GoogleAuthSerializer(serializers.Serializer):
    google_token = serializers.CharField(required=True)
    email = serializers.EmailField()
    username = serializers.CharField(max_length=150)
    first_name = serializers.CharField(max_length=150, required=False, allow_blank=True, default='')
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True, default='')
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True, default='')
    google_id = serializers.CharField(required=False, allow_blank=True, default='')
    
    def validate_google_token(self, value):
        """
        Verify the Google token is valid
        You can integrate with google-auth library here
        """
        # TODO: Verify token with Google's API
        # from google.oauth2 import id_token
        # from google.auth.transport import requests
        # try:
        #     idinfo = id_token.verify_oauth2_token(
        #         value, requests.Request(), CLIENT_ID
        #     )
        #     return idinfo
        # except ValueError:
        #     raise serializers.ValidationError("Invalid Google token")
        
        return value
    
    def validate_phone(self, value):
        """Optional phone validation for Google auth"""
        if value:
            phone_clean = re.sub(r'\D', '', value)
            if len(phone_clean) < 10 or len(phone_clean) > 15:
                raise serializers.ValidationError("Phone number must be between 10-15 digits")
            return phone_clean
        return value