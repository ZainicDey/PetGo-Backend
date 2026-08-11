from django.urls import path
from rest_framework.routers import SimpleRouter
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

router = SimpleRouter(trailing_slash=False)
router.register(r'foster-house-finder/reviews', HouseReviewViewSet, basename='house-review')
router.register(r'foster-house-finder/replies', HouseReviewReplyViewSet, basename='house-reply')

urlpatterns = [
    path('foster-house-finder/tags', TagListCreateView.as_view()),
    path('foster-house-finder/tags/<uuid:uuid>', TagDetailView.as_view()),
    path('foster-house-finder/houses', HouseListCreateView.as_view()),
    path('foster-house-finder/houses/<uuid:uuid>', HouseDetailView.as_view()),
    path('foster-house-finder/appointments', AppointmentListView.as_view()),
    path('foster-house-finder/appointments/<uuid:uuid>', AppointmentDetailView.as_view()),
]

urlpatterns += router.urls