from django.urls import path
from . import views
from rest_framework.routers import SimpleRouter

router = SimpleRouter(trailing_slash=False)
router.register(r'vet-finder/reviews', views.HospitalReviewViewSet, basename='vet-review')
router.register(r'vet-finder/replies', views.HospitalReviewReplyViewSet, basename='vet-reply')

urlpatterns = [
    path('vet-finder/tags', views.TagListCreateView.as_view()),
    path('vet-finder/tags/<uuid:uuid>', views.TagDetailView.as_view()),

    path('vet-finder/hospitals', views.HospitalListCreateView.as_view()),
    path('vet-finder/hospitals/<uuid:uuid>', views.HospitalDetailView.as_view()),

    path('vet-finder/appointments', views.AppointmentListView.as_view()),
    path('vet-finder/appointments/<uuid:uuid>', views.AppointmentDetailView.as_view()),
]

urlpatterns += router.urls