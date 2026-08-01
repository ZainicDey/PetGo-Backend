from django.urls import path
from rest_framework.routers import SimpleRouter
from . import views

router = SimpleRouter(trailing_slash=False)
router.register(r'marketing/coupon', views.CouponViewSet, basename='coupon')

urlpatterns = router.urls
