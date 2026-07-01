from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from .models import FosterHouseTag, House, Appointment, HouseReview, HouseReviewReply
from .serializers import (
    FosterHouseTagSerializer,
    HouseListSerializer,
    HouseDetailSerializer,
    HouseCreateUpdateSerializer,
    AppointmentCreateSerializer,
    AppointmentDetailSerializer,
    HouseReviewSerializer,
    HouseReviewReplySerializer
)


# =============== TAG VIEWS ===============

class TagListCreateView(generics.ListCreateAPIView):
    """
    GET  → list all available tags
    POST → create a new tag  {"name": "dental care"}
    """
    queryset = FosterHouseTag.objects.all()
    serializer_class = FosterHouseTagSerializer

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
    queryset = FosterHouseTag.objects.all()
    serializer_class = FosterHouseTagSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAdminUser()]


# =============== HOUSE VIEWS ===============

class HouseListCreateView(generics.ListCreateAPIView):
    """
    GET  → list all houses (lightweight, no veterinarians)
    POST → create a house with nested veterinarians & tag_ids
    """
    queryset = House.objects.prefetch_related('tags').all()
    
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAdminUser()]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return HouseCreateUpdateSerializer
        return HouseListSerializer


class HouseDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    → full house detail (includes veterinarians list)
    PUT    → full update
    PATCH  → partial update
    DELETE → delete house (cascades to veterinarians)
    """
    queryset = House.objects.prefetch_related('tags', 'veterinarians').all()

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAdminUser()]

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return HouseCreateUpdateSerializer
        return HouseDetailSerializer

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

class AppointmentDetailView(generics.RetrieveAPIView):
    serializer_class = AppointmentDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Appointment.objects.all()
        return Appointment.objects.filter(user=self.request.user)

from rest_framework.viewsets import ModelViewSet
from vet_finder.views import IsOwnerOrReadOnly


class HouseReviewViewSet(ModelViewSet):
    queryset = HouseReview.objects.select_related('user', 'house') \
                                  .prefetch_related('house_review_replies__user')
    serializer_class = HouseReviewSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated(), IsOwnerOrReadOnly()]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class HouseReviewReplyViewSet(ModelViewSet):
    queryset = HouseReviewReply.objects.select_related('user', 'review').all()
    serializer_class = HouseReviewReplySerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated(), IsOwnerOrReadOnly()]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

