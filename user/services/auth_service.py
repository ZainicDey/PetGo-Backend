# user/services/auth_service.py
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.db import transaction
from user.models import UserModel, TemporaryUser
from django.utils import timezone
import random
import re
import logging

logger = logging.getLogger(__name__)

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
        from user.services.sms_service import SMSService
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
    
    # =============== GOOGLE AUTH METHODS ===============
    
    @staticmethod
    def login_or_register_with_google(google_token):
        """
        Verify Google token and login/register user
        
        Args:
            google_token: Google ID Token from frontend
            
        Returns:
            dict with user info and tokens
        """
        # ✅ FIXED: Import from the correct module
        from .google_service import GoogleAuthService
        
        # Step 1: Verify the token with Google
        try:
            google_data = GoogleAuthService.verify_google_id_token(google_token)
        except ValueError as e:
            raise ValueError(f"Google authentication failed: {str(e)}")
        
        # google_data now contains VERIFIED user info:
        # {
        #     'google_id': '1234567890',
        #     'email': 'john@gmail.com',
        #     'first_name': 'John',
        #     'last_name': 'Doe',
        #     'name': 'John Doe',
        #     'picture': 'https://...',
        #     'email_verified': True
        # }
        
        # Step 2: Check if user exists by email
        try:
            user = User.objects.get(email=google_data['email'])
            is_new_user = False
            
            # Update user info if needed
            updated = False
            if not user.first_name and google_data['first_name']:
                user.first_name = google_data['first_name']
                updated = True
            if not user.last_name and google_data['last_name']:
                user.last_name = google_data['last_name']
                updated = True
            
            if updated:
                user.save()
            
            # Ensure UserModel exists
            UserModel.objects.get_or_create(
                user=user,
                defaults={
                    'phone': '',
                    'is_phone_verified': False
                }
            )
            
        except User.DoesNotExist:
            # Step 3: Create new user
            is_new_user = True
            
            with transaction.atomic():
                # Generate unique username from email
                base_username = google_data['email'].split('@')[0]
                base_username = re.sub(r'[^a-zA-Z0-9_]', '_', base_username)
                
                username = base_username
                counter = 1
                while User.objects.filter(username=username).exists():
                    username = f"{base_username}{counter}"
                    counter += 1
                
                # Create user
                user = User.objects.create(
                    username=username,
                    email=google_data['email'],
                    first_name=google_data['first_name'],
                    last_name=google_data['last_name'],
                    password='!'  # Temporary placeholder
                )
                
                # Set unusable password (can't login with password)
                user.set_unusable_password()
                user.save()
                
                # Create UserModel
                UserModel.objects.create(
                    user=user,
                    phone='',  # Google doesn't provide phone
                    is_phone_verified=False
                )
        
        # Step 4: Return result
        return {
            'user': user,
            'is_new': is_new_user,
            'google_data': google_data,
            'message': 'Logged in with Google' if not is_new_user else 'Registered with Google'
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