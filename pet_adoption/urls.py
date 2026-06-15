from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import PetAdoptionView

router = SimpleRouter(trailing_slash=False)
router.register(r'pet-adoption', PetAdoptionView, basename='pet-adoption')

urlpatterns = router.urls