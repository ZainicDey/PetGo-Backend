# services/auth_service.py
from django.contrib.auth.models import User
from django.db import transaction
from ..models import UserModel, TemporaryUser
import random
from django.utils import timezone

class AuthenticationService:
    
    @staticmethod
    def initiate_sms_registration(email, username, phone, password, first_name='', last_name=''):
        """Step 1: Create temporary user and send OTP"""
        
        # Check if user already exists
        if User.objects.filter(email=email).exists():
            raise ValueError("User with this email already exists")
        
        # Generate OTP
        otp = str(random.randint(100000, 999999))
        
        # Delete any existing temporary registrations for this email
        TemporaryUser.objects.filter(email=email).delete()
        
        # Create temporary user
        temp_user = TemporaryUser.objects.create(
            email=email,
            username=username,
            phone=phone,
            password=password,  # Should be hashed before storing
            first_name=first_name,
            last_name=last_name,
            auth_method='sms_otp',
            otp=otp
        )
        
        # Send OTP via SMS
        SMSService.send_otp(phone, otp)
        
        return {
            'request_id': str(temp_user.request_id),
            'message': 'OTP sent to your phone'
        }
    
    @staticmethod
    def verify_sms_otp(request_id, otp_input):
        """Step 2: Verify OTP and create actual user"""
        
        try:
            temp_user = TemporaryUser.objects.get(
                request_id=request_id,
                is_verified=False
            )
        except TemporaryUser.DoesNotExist:
            raise ValueError("Invalid or expired registration request")
        
        # Check OTP expiration
        if temp_user.is_otp_expired():
            temp_user.delete()
            raise ValueError("OTP has expired. Please register again")
        
        # Verify OTP
        if temp_user.otp != otp_input:
            raise ValueError("Invalid OTP")
        
        # Create actual user
        with transaction.atomic():
            # Create Django User
            user = User.objects.create_user(
                username=temp_user.username,
                email=temp_user.email,
                password=temp_user.password,
                first_name=temp_user.first_name,
                last_name=temp_user.last_name
            )
            
            # Create UserModel
            user_model = UserModel.objects.create(
                user=user,
                phone=temp_user.phone,
                is_phone_verified=True
            )
            
            # Mark temporary user as verified
            temp_user.is_verified = True
            temp_user.save()
            
            # Clean up temporary record
            temp_user.delete()
        
        return {
            'user_id': user.id,
            'message': 'Registration successful'
        }
    
    @staticmethod
    def initiate_google_auth(email, username, first_name, last_name, phone):
        """Handle Google OAuth registration - direct creation"""
        
        # Check if user exists
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            
            # Update existing user info
            user.first_name = first_name
            user.last_name = last_name
            user.save()
            
            # Update or create UserModel
            user_model, created = UserModel.objects.update_or_create(
                user=user,
                defaults={'phone': phone}
            )
            
            return {
                'user_id': user.id,
                'is_new': False,
                'message': 'Login successful'
            }
        
        # Create new user from Google auth
        with transaction.atomic():
            user = User.objects.create_user(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=User.objects.make_random_password()  # No password for Google auth
            )
            
            user_model = UserModel.objects.create(
                user=user,
                phone=phone,
                is_phone_verified=False  # Phone not verified with Google auth
            )
        
        return {
            'user_id': user.id,
            'is_new': True,
            'message': 'Google registration successful'
        }