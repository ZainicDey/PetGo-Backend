from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAdminUser
from .models import Tag, House
from .serializers import (
    TagSerializer,
    HouseSerializer,
    HouseDetailSerializer,
    HouseCreateUpdateSerializer,
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
        return HouseSerializer


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
