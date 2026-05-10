# user/services/token_service.py
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from rest_framework_simplejwt.exceptions import TokenError
import logging

logger = logging.getLogger(__name__)

class TokenService:
    """
    Service for generating and managing JWT tokens
    """
    
    @staticmethod
    def get_tokens_for_user(user):
        """
        Generate JWT tokens for a user
        
        Args:
            user: User model instance
            
        Returns:
            dict: Contains access token, refresh token, and user data
            
        Example:
            {
                'access': 'eyJhbGciOiJIUzI1NiIs...',
                'refresh': 'eyJhbGciOiJIUzI1NiIs...',
                'user': {
                    'id': 1,
                    'email': 'john@example.com',
                    'username': 'john_doe',
                    'first_name': 'John',
                    'last_name': 'Doe',
                }
            }
        """
        try:
            # Create refresh token
            refresh = RefreshToken.for_user(user)
            
            # Add custom claims to the access token
            refresh['email'] = user.email
            refresh['username'] = user.username
            refresh['first_name'] = user.first_name
            refresh['last_name'] = user.last_name
            
            # Add UserModel data if available
            try:
                user_model = user.userinfo
                refresh['phone'] = user_model.phone
                refresh['is_phone_verified'] = user_model.is_phone_verified
            except Exception:
                refresh['phone'] = None
                refresh['is_phone_verified'] = False
            
            # Get access token
            access_token = refresh.access_token
            
            # Add same claims to access token
            access_token['email'] = user.email
            access_token['username'] = user.username
            access_token['first_name'] = user.first_name
            access_token['last_name'] = user.last_name
            
            return {
                'refresh': str(refresh),
                'access': str(access_token),
                'user': TokenService.get_user_data(user)
            }
            
        except Exception as e:
            logger.error(f"Failed to generate tokens for user {user.id}: {str(e)}")
            raise Exception("Failed to generate authentication tokens")
    
    @staticmethod
    def get_user_data(user):
        """
        Get standardized user data dictionary
        
        Args:
            user: User model instance
            
        Returns:
            dict: User data without sensitive information
        """
        data = {
            'id': user.id,
            'email': user.email,
            'username': user.username,
            'first_name': user.first_name or '',
            'last_name': user.last_name or '',
            'full_name': user.get_full_name() or user.username,
            'is_active': user.is_active,
            'date_joined': user.date_joined.isoformat() if user.date_joined else None,
        }
        
        # Add UserModel data
        try:
            user_model = user.userinfo
            data['phone'] = user_model.phone or ''
            data['is_phone_verified'] = user_model.is_phone_verified
            data['has_phone'] = bool(user_model.phone)
        except Exception:
            data['phone'] = ''
            data['is_phone_verified'] = False
            data['has_phone'] = False
        
        return data
    
    @staticmethod
    def refresh_access_token(refresh_token_str):
        """
        Refresh an access token using a refresh token
        
        Args:
            refresh_token_str (str): The refresh token string
            
        Returns:
            dict: New access token (and optionally new refresh token)
            
        Raises:
            ValueError: If the refresh token is invalid or expired
        """
        try:
            # Create RefreshToken object from string
            refresh = RefreshToken(refresh_token_str)
            
            # Generate new access token
            access_token = str(refresh.access_token)
            
            response = {
                'access': access_token,
            }
            
            # If token rotation is enabled, also return new refresh token
            from django.conf import settings
            if getattr(settings, 'SIMPLE_JWT', {}).get('ROTATE_REFRESH_TOKENS', False):
                # Blacklist old token if blacklist app is enabled
                if getattr(settings, 'SIMPLE_JWT', {}).get('BLACKLIST_AFTER_ROTATION', False):
                    try:
                        refresh.blacklist()
                    except Exception:
                        pass
                
                # Create new refresh token
                new_refresh = RefreshToken.for_user(refresh.user)
                response['refresh'] = str(new_refresh)
            
            return response
            
        except TokenError as e:
            logger.error(f"Token refresh failed: {str(e)}")
            raise ValueError("Invalid or expired refresh token")
        except Exception as e:
            logger.error(f"Unexpected error refreshing token: {str(e)}")
            raise ValueError("Failed to refresh token")
    
    @staticmethod
    def blacklist_token(refresh_token_str):
        """
        Blacklist a refresh token (for logout)
        
        Args:
            refresh_token_str (str): The refresh token to blacklist
            
        Returns:
            bool: True if successful
            
        Raises:
            ValueError: If token is invalid
        """
        try:
            token = RefreshToken(refresh_token_str)
            token.blacklist()
            logger.info("Token blacklisted successfully")
            return True
            
        except TokenError as e:
            logger.error(f"Token blacklist failed: {str(e)}")
            raise ValueError("Invalid token")
        except AttributeError:
            # Blacklist app might not be installed
            logger.warning("Blacklist app not installed. Token not blacklisted.")
            raise ValueError("Token blacklisting is not enabled")
        except Exception as e:
            logger.error(f"Unexpected error blacklisting token: {str(e)}")
            raise ValueError("Failed to blacklist token")
    
    @staticmethod
    def get_token_info(refresh_token_str):
        """
        Get information about a refresh token
        
        Args:
            refresh_token_str (str): The refresh token
            
        Returns:
            dict: Token payload information
        """
        try:
            token = RefreshToken(refresh_token_str)
            return {
                'user_id': token.get('user_id'),
                'email': token.get('email', ''),
                'username': token.get('username', ''),
                'exp': token.get('exp'),
                'iat': token.get('iat'),
                'jti': token.get('jti'),
            }
        except Exception as e:
            logger.error(f"Failed to get token info: {str(e)}")
            raise ValueError("Invalid token")
    
    @staticmethod
    def generate_token_response(user):
        """
        Generate a complete authentication response for a user
        
        This is a convenience method that combines token generation
        and user data into the standard response format.
        
        Args:
            user: User model instance
            
        Returns:
            dict: Complete auth response with tokens and user data
        """
        tokens = TokenService.get_tokens_for_user(user)
        
        return {
            'success': True,
            'data': {
                'tokens': {
                    'access': tokens['access'],
                    'refresh': tokens['refresh'],
                },
                'user': tokens['user']
            }
        }