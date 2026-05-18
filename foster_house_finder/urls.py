from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
    TagListCreateView,
    TagDetailView,
    HouseListCreateView,
    HouseDetailView,
    AppointmentListView,
    AppointmentDetailView,
    HouseReviewViewSet,
    HouseReviewReplyViewSet,
)

router = DefaultRouter()
router.register(r'foster-house-finder/reviews', HouseReviewViewSet, basename='house-review')
router.register(r'foster-house-finder/replies', HouseReviewReplyViewSet, basename='house-reply')

urlpatterns = [
    path('foster-house-finder/tags/', TagListCreateView.as_view(), name='tag-list-create'),
    path('foster-house-finder/tags/<int:pk>/', TagDetailView.as_view(), name='tag-detail'),
    path('foster-house-finder/houses/', HouseListCreateView.as_view(), name='house-list-create'),
    path('foster-house-finder/houses/<int:pk>/', HouseDetailView.as_view(), name='house-detail'),
    path('foster-house-finder/appointments/', AppointmentListView.as_view(), name='appointment-list-create'),
    path('foster-house-finder/appointments/<int:pk>/', AppointmentDetailView.as_view(), name='appointment-detail'),
]

urlpatterns += router.urls