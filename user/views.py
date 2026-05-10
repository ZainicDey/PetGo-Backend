# views.py (FIXED)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User  # ← ADD THIS IMPORT
from .services.auth_service import AuthenticationService
from .services.token_service import TokenService
from .serializers import (
    RegisterSerializer,
    OTPVerifySerializer,
    GoogleAuthSerializer,
    EmailLoginSerializer,
    PhoneLoginSerializer,
    GoogleLoginSerializer,
    CustomTokenObtainPairSerializer
)
from drf_spectacular.utils import extend_schema

import logging

logger = logging.getLogger(__name__)


# =============== JWT TOKEN VIEWS ===============

class CustomTokenObtainPairView(TokenObtainPairView):
    """Login with email/password to get JWT tokens"""
    serializer_class = CustomTokenObtainPairSerializer
    
    def post(self, request, *args, **kwargs):
        """POST: { "username": "anik", "password": "anikanik" }"""
        request_data = request.data.copy()
        print(request.data)
        try:
            user = User.objects.get(username=request_data.get('username', ''))
            print(user.email)
            request_data['username'] = user.username
        except User.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Invalid username or password'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        request._full_data = request_data
        return super().post(request, *args, **kwargs)


class TokenRefreshViewCustom(TokenRefreshView):
    """Refresh an expired access token"""
    
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            return Response({
                'success': True,
                'data': response.data
            }, status=status.HTTP_200_OK)
        
        return Response({
            'success': False,
            'error': 'Invalid or expired refresh token'
        }, status=status.HTTP_401_UNAUTHORIZED)

class LogoutView(APIView):
    """Logout by blacklisting the refresh token"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if not refresh_token:
                return Response({
                    'success': False,
                    'error': 'Refresh token is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            token = RefreshToken(refresh_token)
            token.blacklist()
            
            return Response({
                'success': True,
                'message': 'Logged out successfully'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'success': False,
                'error': 'Invalid token'
            }, status=status.HTTP_400_BAD_REQUEST)


# =============== REGISTRATION VIEWS ===============
@extend_schema(
    request=RegisterSerializer,
)
class RegisterView(APIView):
    """Register with phone + password (Step 1: Get OTP)"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            result = AuthenticationService.initiate_sms_registration(
                email=serializer.validated_data['email'],
                username=serializer.validated_data['username'],
                phone=serializer.validated_data['phone'],
                password=serializer.validated_data['password'],
                first_name=serializer.validated_data.get('first_name', ''),
                last_name=serializer.validated_data.get('last_name', '')
            )
            
            return Response({
                'success': True,
                'data': {
                    'request_id': result['request_id'],
                    'message': result['message'],
                    'expires_in': result['expires_in']
                }
            }, status=status.HTTP_200_OK)
            
        except ValueError as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    request=OTPVerifySerializer,
)
class VerifyOTPView(APIView):
    """Register with phone + password (Step 2: Verify OTP & Get JWT)"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            result = AuthenticationService.verify_sms_otp(
                request_id=serializer.validated_data['request_id'],
                otp_input=serializer.validated_data['otp']
            )
            
            tokens = TokenService.get_tokens_for_user(result['user'])
            
            return Response({
                'success': True,
                'message': result['message'],
                'data': {
                    'tokens': {
                        'access': tokens['access'],
                        'refresh': tokens['refresh'],
                    },
                    'user': tokens['user']
                }
            }, status=status.HTTP_200_OK)
            
        except ValueError as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


# =============== GOOGLE AUTH VIEWS (FIXED) ===============

@extend_schema(
    request=GoogleAuthSerializer,
)
class GoogleRegisterView(APIView):
    """
    Register/Login with Google OAuth
    
    Handles BOTH registration and login.
    Verifies Google token before creating/logging in user.
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        """
        POST: { "credential": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9..." }
        """
        serializer = GoogleAuthSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # ✅ FIXED: Use login_or_register_with_google (verifies token!)
            result = AuthenticationService.login_or_register_with_google(
                google_token=serializer.validated_data['credential']
            )
            
            # Generate JWT tokens
            tokens = TokenService.get_tokens_for_user(result['user'])
            
            return Response({
                'success': True,
                'message': result['message'],
                'is_new_user': result['is_new'],
                'data': {
                    'tokens': {
                        'access': tokens['access'],
                        'refresh': tokens['refresh'],
                    },
                    'user': tokens['user'],
                    'google_profile': {
                        'name': result['google_data'].get('name', ''),
                        'picture': result['google_data'].get('picture', ''),
                    }
                }
            }, status=status.HTTP_200_OK)
            
        except ValueError as e:
            logger.error(f"Google auth error: {str(e)}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            logger.error(f"Unexpected Google auth error: {str(e)}")
            return Response({
                'success': False,
                'error': 'Authentication failed. Please try again.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@extend_schema(
    request=GoogleLoginSerializer,
)
class GoogleLoginView(APIView):
    """
    Login with Google OAuth
    
    Same as GoogleRegisterView - Google auth handles both login and registration.
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        """
        POST: { "google_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9..." }
        """
        serializer = GoogleLoginSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # ✅ FIXED: Use login_or_register_with_google (verifies token!)
            result = AuthenticationService.login_or_register_with_google(
                google_token=serializer.validated_data['google_token']
            )
            
            # Generate JWT tokens
            tokens = TokenService.get_tokens_for_user(result['user'])
            
            return Response({
                'success': True,
                'message': result['message'],
                'is_new_user': result['is_new'],
                'data': {
                    'tokens': {
                        'access': tokens['access'],
                        'refresh': tokens['refresh'],
                    },
                    'user': tokens['user'],
                    'google_profile': {
                        'name': result['google_data'].get('name', ''),
                        'picture': result['google_data'].get('picture', ''),
                    }
                }
            }, status=status.HTTP_200_OK)
            
        except ValueError as e:
            logger.error(f"Google login error: {str(e)}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            logger.error(f"Unexpected Google login error: {str(e)}")
            return Response({
                'success': False,
                'error': 'Authentication failed. Please try again.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# =============== LOGIN VIEWS ===============

@extend_schema(
    request=EmailLoginSerializer,
)
class EmailLoginView(APIView):
    """Login with email and password - Returns JWT"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = EmailLoginSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            result = AuthenticationService.login_with_password(
                email=serializer.validated_data['email'],
                password=serializer.validated_data['password']
            )
            
            tokens = TokenService.get_tokens_for_user(result['user'])
            
            return Response({
                'success': True,
                'message': result['message'],
                'data': {
                    'tokens': {
                        'access': tokens['access'],
                        'refresh': tokens['refresh'],
                    },
                    'user': tokens['user']
                }
            }, status=status.HTTP_200_OK)
            
        except ValueError as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_401_UNAUTHORIZED)


@extend_schema(
    request=PhoneLoginSerializer,
)
class PhoneLoginView(APIView):
    """Login with phone and password - Returns JWT"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = PhoneLoginSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            result = AuthenticationService.login_with_phone(
                phone=serializer.validated_data['phone'],
                password=serializer.validated_data['password']
            )
            
            tokens = TokenService.get_tokens_for_user(result['user'])
            
            return Response({
                'success': True,
                'message': result['message'],
                'data': {
                    'tokens': {
                        'access': tokens['access'],
                        'refresh': tokens['refresh'],
                    },
                    'user': tokens['user']
                }
            }, status=status.HTTP_200_OK)
            
        except ValueError as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_401_UNAUTHORIZED)


# =============== USER PROFILE ===============

class UserProfileView(APIView):
    """Get current user profile - Protected by JWT"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """GET: Headers: Authorization: Bearer eyJ..."""
        user_data = TokenService.get_user_data(request.user)
        
        return Response({
            'success': True,
            'data': user_data
        }, status=status.HTTP_200_OK)