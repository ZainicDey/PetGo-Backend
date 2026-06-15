from django.urls import path
from rest_framework.routers import SimpleRouter
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

router = SimpleRouter(trailing_slash=False)
router.register(r'training-grooming/reviews', TrainingGroomingReviewViewSet, basename='training-grooming-review')
router.register(r'training-grooming/replies', TrainingGroomingReviewReplyViewSet, basename='training-grooming-reply')

urlpatterns = [
    path('training-grooming/tags', TagListCreateView.as_view()),
    path('training-grooming/tags/<int:pk>', TagDetailView.as_view()),
    path('training-grooming', TrainingGroomingListCreateView.as_view()),
    path('training-grooming/<int:pk>', TrainingGroomingDetailView.as_view()),
    path('training-grooming/appointments', AppointmentListView.as_view()),
    path('training-grooming/appointments/<int:pk>', AppointmentDetailView.as_view()),
]

urlpatterns += router.urls