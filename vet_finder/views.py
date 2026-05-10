from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAdminUser
from .models import Tag, Hospital
from .serializers import (
    TagSerializer,
    HospitalListSerializer,
    HospitalDetailSerializer,
    HospitalCreateUpdateSerializer,
)


# =============== TAG VIEWS ===============

class TagListCreateView(generics.ListCreateAPIView):
    """
    GET  → list all available tags
    POST → create a new tag  {"name": "dental care"}
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

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
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

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
