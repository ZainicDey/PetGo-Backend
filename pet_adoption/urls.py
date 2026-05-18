from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PetAdoptionView

router = DefaultRouter()
router.register(r'pet-adoption', PetAdoptionView, basename='pet-adoption')

urlpatterns = [
    path('', include(router.urls)),
]