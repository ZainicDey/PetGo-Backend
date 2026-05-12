# ✅ FIXED VERSION with better exception handling:

import logging
from django.conf import settings

# Check if google-auth is installed
try:
    from google.oauth2 import id_token
    from google.auth.transport import requests as google_requests
    from google.auth.exceptions import GoogleAuthError  # Add this
    GOOGLE_AUTH_AVAILABLE = True
except ImportError:
    GOOGLE_AUTH_AVAILABLE = False
    logger.warning("google-auth library not installed. Google auth will not work.")

logger = logging.getLogger(__name__)

class GoogleAuthService:
    """Service for verifying Google OAuth tokens"""
    
    @staticmethod
    def verify_google_id_token(token):
        """
        Verify Google ID Token from Google Identity Services
        """
        if not GOOGLE_AUTH_AVAILABLE:
            raise ValueError("Google authentication is not configured. Install google-auth package.")
        
        # Validate settings
        if not hasattr(settings, 'GOOGLE_CLIENT_ID') or not settings.GOOGLE_CLIENT_ID:
            raise ValueError("GOOGLE_CLIENT_ID is not configured in settings")
        
        try:
            # Verify the token with Google's servers
            idinfo = id_token.verify_oauth2_token(
                token,
                google_requests.Request(),
                settings.GOOGLE_CLIENT_ID,
                clock_skew_in_seconds=10
            )
            
            # Validate issuer
            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Wrong issuer.')
            
            # Validate email is verified
            if not idinfo.get('email_verified', False):
                raise ValueError('Email not verified by Google')
            
            # Return verified user data
            return {
                'success': True,
                'google_id': idinfo['sub'],
                'email': idinfo['email'],
                'first_name': idinfo.get('given_name', ''),
                'last_name': idinfo.get('family_name', ''),
                'name': idinfo.get('name', ''),
                'picture': idinfo.get('picture', ''),
                'email_verified': True
            }
            
        except ValueError as e:
            # Token validation errors
            logger.error(f"Google token validation failed: {str(e)}")
            raise ValueError(f"Invalid Google token: {str(e)}")
            
        except GoogleAuthError as e:
            # Google library specific errors
            logger.error(f"Google auth library error: {str(e)}")
            raise ValueError(f"Authentication failed: {str(e)}")
            
        except Exception as e:
            # Unexpected errors
            logger.error(f"Unexpected Google verification error: {str(e)}")
            raise ValueError("Failed to verify Google token. Please try again.")