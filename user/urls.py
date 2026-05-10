# urls.py
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    # =============== JWT AUTH ENDPOINTS ===============
    
    # Standard JWT login (email/password) - Returns access + refresh tokens
    path('auth/login/', views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    
    # Refresh access token using refresh token
    path('auth/token/refresh/', views.TokenRefreshViewCustom.as_view(), name='token_refresh'),
    
    # Logout (blacklist refresh token)
    path('auth/logout/', views.LogoutView.as_view(), name='auth_logout'),
    
    # =============== REGISTRATION ENDPOINTS ===============
    
    # Phone registration - Step 1: Get OTP
    path('auth/register/', views.RegisterView.as_view(), name='register'),
    
    # Phone registration - Step 2: Verify OTP & Get JWT
    path('auth/verify-otp/', views.VerifyOTPView.as_view(), name='verify-otp'),
    
    # Google registration/login
    path('auth/google/', views.GoogleRegisterView.as_view(), name='google-auth'),
    
    # =============== ALTERNATIVE LOGIN ENDPOINTS ===============
    
    # Login with email/password (alternative to standard JWT endpoint)
    path('auth/login/email/', views.EmailLoginView.as_view(), name='email-login'),
    
    # Login with phone/password
    path('auth/login/phone/', views.PhoneLoginView.as_view(), name='phone-login'),
    
    # Login with Google
    path('auth/login/google/', views.GoogleLoginView.as_view(), name='google-login'),
    
    # =============== PROTECTED ENDPOINTS ===============
    
    # User profile (requires JWT)
    path('user/profile/', views.UserProfileView.as_view(), name='user-profile'),
]