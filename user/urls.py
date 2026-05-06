# urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Registration endpoints
    path('auth/register/', views.RegisterView.as_view(), name='register'),
    path('auth/verify-otp/', views.VerifyOTPView.as_view(), name='verify-otp'),
    path('auth/google/register/', views.GoogleRegisterView.as_view(), name='google-register'),
    
    # Login endpoints
    path('auth/login/email/', views.EmailLoginView.as_view(), name='email-login'),
    path('auth/login/phone/', views.PhoneLoginView.as_view(), name='phone-login'),
    path('auth/login/google/', views.GoogleLoginView.as_view(), name='google-login'),
]