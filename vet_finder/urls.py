from django.urls import path
from . import views
from rest_framework.routers import SimpleRouter

router = SimpleRouter(trailing_slash=False)
router.register(r'vet-finder/reviews', views.HospitalReviewViewSet, basename='vet-review')
router.register(r'vet-finder/replies', views.HospitalReviewReplyViewSet, basename='vet-reply')

urlpatterns = [
    path('vet-finder/tags', views.TagListCreateView.as_view()),
    path('vet-finder/tags/<int:pk>', views.TagDetailView.as_view()),

    path('vet-finder/hospitals', views.HospitalListCreateView.as_view()),
    path('vet-finder/hospitals/<int:pk>', views.HospitalDetailView.as_view()),

    path('vet-finder/appointments', views.AppointmentListView.as_view()),
    path('vet-finder/appointments/<int:pk>', views.AppointmentDetailView.as_view()),
]

urlpatterns += router.urls 