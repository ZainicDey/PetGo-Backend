from django.urls import path
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'vet-finder/reviews', views.VetReviewListView, basename='vet-review')


urlpatterns = [
    # Tags
    path('vet-finder/tags/', views.TagListCreateView.as_view(), name='tag-list-create'),
    path('vet-finder/tags/<int:pk>/', views.TagDetailView.as_view(), name='tag-detail'),

    # Hospitals
    path('vet-finder/hospitals/', views.HospitalListCreateView.as_view(), name='hospital-list-create'),
    path('vet-finder/hospitals/<int:pk>/', views.HospitalDetailView.as_view(), name='hospital-detail'),

    # Appointments
    path('vet-finder/appointments/', views.AppointmentListView.as_view(), name='appointment-list-create'),
]
