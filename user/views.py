# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from django.contrib.auth import login
from user.services.auth_service import AuthenticationService
from user.serializers import (
    RegisterSerializer,
    OTPVerifySerializer,
    GoogleAuthSerializer,
    # EmailLoginSerializer,
    # PhoneLoginSerializer,
    # GoogleLoginSerializer
)
import logging

logger = logging.getLogger(__name__)

class BaseAuthView(APIView):
    """Base class for auth views"""
    
    def get_tokens_for_user(self, user):
        """Generate auth token for user"""
        token, created = Token.objects.get_or_create(user=user)
        return {
            'token': token.key,
            'user_id': user.id,
            'email': user.email,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
        }


# =============== REGISTRATION VIEWS ===============

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
                'data': result
            }, status=status.HTTP_200_OK)
            
        except ValueError as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class VerifyOTPView(APIView):
    """Register with phone + password (Step 2: Verify OTP)"""
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
            
            # Generate tokens
            user_data = BaseAuthView().get_tokens_for_user(result['user'])
            
            return Response({
                'success': True,
                'message': result['message'],
                'data': user_data
            }, status=status.HTTP_200_OK)
            
        except ValueError as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class GoogleRegisterView(APIView):
    """Register/Login with Google OAuth"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = GoogleAuthSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            result = AuthenticationService.register_with_google(
                email=serializer.validated_data['email'],
                username=serializer.validated_data.get('username', serializer.validated_data['email'].split('@')[0]),
                first_name=serializer.validated_data.get('first_name', ''),
                last_name=serializer.validated_data.get('last_name', ''),
                phone=serializer.validated_data.get('phone', ''),
                google_id=serializer.validated_data.get('google_id', '')
            )
            
            user_data = BaseAuthView().get_tokens_for_user(result['user'])
            
            return Response({
                'success': True,
                'message': result['message'],
                'is_new': result['is_new'],
                'data': user_data
            }, status=status.HTTP_200_OK)
            
        except ValueError as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


# =============== LOGIN VIEWS ===============

class EmailLoginView(APIView):
    """Login with email and password"""
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
            
            user_data = BaseAuthView().get_tokens_for_user(result['user'])
            user_data['is_phone_verified'] = result['is_phone_verified']
            
            return Response({
                'success': True,
                'message': result['message'],
                'data': user_data
            }, status=status.HTTP_200_OK)
            
        except ValueError as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class PhoneLoginView(APIView):
    """Login with phone and password"""
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
            
            user_data = BaseAuthView().get_tokens_for_user(result['user'])
            user_data['is_phone_verified'] = result['is_phone_verified']
            
            return Response({
                'success': True,
                'message': result['message'],
                'data': user_data
            }, status=status.HTTP_200_OK)
            
        except ValueError as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class GoogleLoginView(APIView):
    """Login with Google OAuth (also handles registration if new user)"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = GoogleLoginSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            result = AuthenticationService.login_with_google(
                email=serializer.validated_data['email'],
                google_token=serializer.validated_data['google_token']
            )
            
            user_data = BaseAuthView().get_tokens_for_user(result['user'])
            
            return Response({
                'success': True,
                'message': result['message'],
                'is_new': result['is_new'],
                'data': user_data
            }, status=status.HTTP_200_OK)
            
        except ValueError as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)