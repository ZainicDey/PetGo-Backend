# services/auth_service.py
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.db import transaction
from user.models import UserModel, TemporaryUser
from django.utils import timezone
import random

class AuthenticationService:
    
    # =============== REGISTRATION METHODS ===============
    
    @staticmethod
    def initiate_sms_registration(email, username, phone, password, first_name='', last_name=''):
        """Step 1: Create temporary user and send OTP"""
        
        # Check if user already exists
        if User.objects.filter(email=email).exists():
            raise ValueError("User with this email already exists")
        
        if UserModel.objects.filter(phone=phone).exists():
            raise ValueError("User with this phone already exists")
        
        # Generate OTP
        otp = str(random.randint(100000, 999999))
        
        # Delete any existing temporary registrations for this email
        TemporaryUser.objects.filter(email=email).delete()
        
        # Create temporary user (password should be hashed)
        from django.contrib.auth.hashers import make_password
        temp_user = TemporaryUser.objects.create(
            email=email,
            username=username,
            phone=phone,
            password=make_password(password),
            first_name=first_name,
            last_name=last_name,
            auth_method='sms_otp',
            otp=otp
        )
        
        # Send OTP via SMS
        SMSService.send_otp(phone, otp)
        
        return {
            'request_id': str(temp_user.request_id),
            'message': 'OTP sent to your phone',
            'expires_in': '10 minutes'
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
            user = User.objects.create_user(
                username=temp_user.username,
                email=temp_user.email,
                password=temp_user.password,  # Already hashed
                first_name=temp_user.first_name,
                last_name=temp_user.last_name
            )
            # Set the password properly
            user.password = temp_user.password
            user.save()
            
            # Create UserModel
            user_model = UserModel.objects.create(
                user=user,
                phone=temp_user.phone,
                is_phone_verified=True
            )
            
            # Clean up
            temp_user.is_verified = True
            temp_user.save()
            temp_user.delete()
        
        return {
            'user_id': user.id,
            'user': user,
            'message': 'Registration successful'
        }
    
    @staticmethod
    def register_with_google(email, username, first_name, last_name, phone, google_id):
        """Handle Google OAuth registration"""
        
        # Check if user exists
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            user.first_name = first_name
            user.last_name = last_name
            user.save()
            
            user_model, created = UserModel.objects.update_or_create(
                user=user,
                defaults={
                    'phone': phone,
                    'is_phone_verified': False
                }
            )
            
            return {
                'user': user,
                'is_new': False,
                'message': 'Logged in with Google'
            }
        
        # Create new user
        with transaction.atomic():
            user = User.objects.create_user(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=User.objects.make_random_password()
            )
            
            user_model = UserModel.objects.create(
                user=user,
                phone=phone,
                is_phone_verified=False
            )
        
        return {
            'user': user,
            'is_new': True,
            'message': 'Registration with Google successful'
        }
    
    # =============== LOGIN METHODS ===============
    
    @staticmethod
    def login_with_password(email, password):
        """Login with email and password"""
        
        # First, find the user by email
        try:
            user_by_email = User.objects.get(email=email)
        except User.DoesNotExist:
            raise ValueError("Invalid email or password")
        
        # Authenticate using username (Django's default behavior)
        user = authenticate(
            username=user_by_email.username,
            password=password
        )
        
        if not user:
            raise ValueError("Invalid email or password")
        
        if not user.is_active:
            raise ValueError("Your account has been disabled")
        
        # Check if user has UserModel (phone verified)
        try:
            user_model = user.userinfo
            is_phone_verified = user_model.is_phone_verified
        except UserModel.DoesNotExist:
            is_phone_verified = False
        
        return {
            'user': user,
            'is_phone_verified': is_phone_verified,
            'message': 'Login successful'
        }
    
    @staticmethod
    def login_with_phone(phone, password):
        """Login with phone number and password"""
        
        # Find user by phone
        try:
            user_model = UserModel.objects.get(phone=phone)
            user = user_model.user
        except UserModel.DoesNotExist:
            raise ValueError("Invalid phone or password")
        
        # Authenticate
        user = authenticate(
            username=user.username,
            password=password
        )
        
        if not user:
            raise ValueError("Invalid phone or password")
        
        if not user.is_active:
            raise ValueError("Your account has been disabled")
        
        return {
            'user': user,
            'is_phone_verified': True,
            'message': 'Login successful'
        }
    
    @staticmethod
    def login_with_google(email, google_token):
        """Login with Google OAuth"""
        
        # Verify Google token
        # google_data = GoogleService.verify_token(google_token)
        
        # Find or create user
        try:
            user = User.objects.get(email=email)
            is_new = False
        except User.DoesNotExist:
            # Auto-register if user doesn't exist
            result = AuthenticationService.register_with_google(
                email=email,
                username=email.split('@')[0],  # Or get from Google data
                first_name='',  # Get from Google data
                last_name='',   # Get from Google data
                phone='',       # Get from Google data if available
                google_id=''    # Get from Google data
            )
            user = result['user']
            is_new = True
        
        return {
            'user': user,
            'is_new': is_new,
            'message': 'Google login successful'
        }