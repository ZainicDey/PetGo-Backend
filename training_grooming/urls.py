from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
    TagListCreateView,
    TagDetailView,
    TrainingGroomingListCreateView,
    TrainingGroomingDetailView,
    AppointmentListView,
    AppointmentDetailView,
    TrainingGroomingReviewViewSet,
    TrainingGroomingReviewReplyViewSet,
)

router = DefaultRouter()
router.register(r'training-grooming/reviews', TrainingGroomingReviewViewSet, basename='training-grooming-review')
router.register(r'training-grooming/replies', TrainingGroomingReviewReplyViewSet, basename='training-grooming-reply')

urlpatterns = [
    path('training-grooming/tags/', TagListCreateView.as_view(), name='tag-list-create'),
    path('training-grooming/tags/<int:pk>/', TagDetailView.as_view(), name='tag-detail'),
    path('training-grooming/', TrainingGroomingListCreateView.as_view(), name='training-grooming-list-create'),
    path('training-grooming/<int:pk>/', TrainingGroomingDetailView.as_view(), name='training-grooming-detail'),
    path('training-grooming/appointments/', AppointmentListView.as_view(), name='appointment-list-create'),
    path('training-grooming/appointments/<int:pk>/', AppointmentDetailView.as_view(), name='appointment-detail'),
]

urlpatterns += router.urls