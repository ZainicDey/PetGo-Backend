
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from .models import HospitalTag, Hospital, Appointment, HostpitalReview, HostpitalReviewReply
from .serializers import (
    HospitalTagSerializer,
    HospitalListSerializer,
    HospitalDetailSerializer,
    HospitalCreateUpdateSerializer,
    AppointmentCreateSerializer,
    AppointmentDetailSerializer,
    VetReviewSerializer,
    VetReviewReplySerializer,
)


# =============== TAG VIEWS ===============

class TagListCreateView(generics.ListCreateAPIView):
    """
    GET  → list all available tags
    POST → create a new tag  {"name": "dental care"}
    """
    queryset = HospitalTag.objects.all()
    serializer_class = HospitalTagSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAdminUser()]


class TagDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    → retrieve a single tag
    PUT    → full update
    PATCH  → partial update
    DELETE → delete tag
    """
    queryset = HospitalTag.objects.all()
    serializer_class = HospitalTagSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAdminUser()]


# =============== HOSPITAL VIEWS ===============

class HospitalListCreateView(generics.ListCreateAPIView):
    """
    GET  → list all hospitals (lightweight, no veterinarians)
    POST → create a hospital with nested veterinarians & tag_ids
    """
    queryset = Hospital.objects.prefetch_related('tags').all()

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAdminUser()]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return HospitalCreateUpdateSerializer
        return HospitalListSerializer


class HospitalDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    → full hospital detail (includes veterinarians list)
    PUT    → full update
    PATCH  → partial update
    DELETE → delete hospital (cascades to veterinarians)
    """
    queryset = Hospital.objects.prefetch_related('tags', 'veterinarians').all()

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAdminUser()]

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return HospitalCreateUpdateSerializer
        return HospitalDetailSerializer

class AppointmentListView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Appointment.objects.all()
        return Appointment.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AppointmentCreateSerializer
        return AppointmentDetailSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

from django.views.generic import ModelViewSet
from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user

class HospitalReviewViewSet(ModelViewSet):
    queryset = HostpitalReview.objects.select_related('user', 'hospital') \
                                  .prefetch_related('vet_review_replies__user')
    serializer_class = HostpitalReviewSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated(), IsOwnerOrReadOnly()]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class HospitalReviewReplyViewSet(ModelViewSet):
    queryset = HostpitalReviewReply.objects.all()
    serializer_class = HostpitalReviewReplySerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated(), IsOwnerOrReadOnly()]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

