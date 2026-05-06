# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from .services.auth_service import AuthenticationService
from .serializers import (
    RegisterSerializer, 
    OTPVerifySerializer, 
    GoogleAuthSerializer
)
from django.contrib.auth import login
from rest_framework.authtoken.models import Token  # If using token auth
import logging

logger = logging.getLogger(__name__)

class InitiateRegistrationView(APIView):
    """Step 1: Register and receive OTP"""
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
                'data': result
            }, status=status.HTTP_200_OK)
            
        except ValueError as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            return Response({
                'success': False,
                'error': 'Something went wrong. Please try again.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class VerifyOTPView(APIView):
    """Step 2: Verify OTP and complete registration"""
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
            
            # Generate auth token if using token authentication
            from django.contrib.auth import get_user_model
            User = get_user_model()
            user = User.objects.get(id=result['user_id'])
            token, _ = Token.objects.get_or_create(user=user)
            
            return Response({
                'success': True,
                'data': {
                    'message': result['message'],
                    'token': token.key,
                    'user_id': result['user_id']
                }
            }, status=status.HTTP_200_OK)
            
        except ValueError as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"OTP verification error: {str(e)}")
            return Response({
                'success': False,
                'error': 'Something went wrong. Please try again.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GoogleAuthView(APIView):
    """Handle Google OAuth registration/login"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = GoogleAuthSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Verify Google token first (optional but recommended)
            # google_info = verify_google_token(serializer.validated_data['google_token'])
            
            result = AuthenticationService.initiate_google_auth(
                email=serializer.validated_data['email'],
                username=serializer.validated_data['username'],
                first_name=serializer.validated_data.get('first_name', ''),
                last_name=serializer.validated_data.get('last_name', ''),
                phone=serializer.validated_data.get('phone', '')
            )
            
            # Generate auth token
            from django.contrib.auth import get_user_model
            User = get_user_model()
            user = User.objects.get(id=result['user_id'])
            token, _ = Token.objects.get_or_create(user=user)
            
            return Response({
                'success': True,
                'data': {
                    'message': result['message'],
                    'token': token.key,
                    'user_id': result['user_id'],
                    'is_new': result['is_new']
                }
            }, status=status.HTTP_200_OK)
            
        except ValueError as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Google auth error: {str(e)}")
            return Response({
                'success': False,
                'error': 'Authentication failed. Please try again.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)