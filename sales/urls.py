from django.urls import path
from rest_framework.routers import SimpleRouter
from . import views

router = SimpleRouter(trailing_slash=False)
router.register(r'sales/order', views.OrderViewSet, basename='order')
router.register(r'sales/order-item', views.OrderItemViewSet, basename='order-item')

urlpatterns = router.urls
