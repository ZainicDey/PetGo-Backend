from django.urls import path
from . import views
from rest_framework.routers import SimpleRouter

router = SimpleRouter(trailing_slash=False)
router.register(r'inventory/category', views.CategoryView, basename='category')
router.register(r'inventory/brand', views.BrandView, basename='brand')
router.register(r'inventory/product', views.ProductView, basename='product')

urlpatterns = router.urls