from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from .models import TrainingGrooming,Appointment,TrainingGroomingReview,TrainingGroomingReviewReply
from .serializers import (
    TrainingGroomingSerializer,
    TrainingGroomingDetailSerializer,
    TrainingGroomingCreateUpdateSerializer,
    AppointmentCreateSerializer,
    AppointmentDetailSerializer,
    TrainingGroomingReviewSerializer,
    TrainingGroomingReviewReplySerializer
)


# =============== TAG VIEWS ===============

class TagListCreateView(generics.ListCreateAPIView):
    """
    GET  → list all available tags
    POST → create a new tag  {"name": "dental care"}
    """
    queryset = TrainingGrooming.objects.all()
    serializer_class = TrainingGroomingSerializer

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
    queryset = TrainingGrooming.objects.all()
    serializer_class = TrainingGroomingSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAdminUser()]


# =============== Trainin & Grooming VIEWS ===============

class TrainingGroomingListCreateView(generics.ListCreateAPIView):
    """
    GET  → list all Training & Grooming (lightweight, no veterinarians)
    POST → create a Training & Grooming with nested veterinarians & tag_ids
    """
    queryset = TrainingGrooming.objects.prefetch_related('tags').all()
    
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAdminUser()]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return TrainingGroomingCreateUpdateSerializer
        return TrainingGroomingSerializer


class TrainingGroomingDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    → full Training & Grooming detail (includes veterinarians list)
    PUT    → full update
    PATCH  → partial update
    DELETE → delete Training & Grooming (cascades to veterinarians)
    """
    queryset = TrainingGrooming.objects.prefetch_related('tags', 'veterinarians').all()

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAdminUser()]

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return TrainingGroomingCreateUpdateSerializer
        return TrainingGroomingDetailSerializer

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


class TrainingGroomingReviewViewSet(ModelViewSet):
    queryset = TrainingGroomingReview.objects.select_related('user', 'grooming') \
                                  .prefetch_related('training_grooming_review_replies__user')
    serializer_class = TrainingGroomingReviewSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated(), IsOwnerOrReadOnly()]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class TrainingGroomingReviewReplyViewSet(ModelViewSet):
    queryset = TrainingGroomingReviewReply.objects.select_related('user', 'review').all()
    serializer_class = TrainingGroomingReviewReplySerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated(), IsOwnerOrReadOnly()]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

