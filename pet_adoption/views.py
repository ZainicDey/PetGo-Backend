from rest_framework.viewsets import ModelViewSet
from .models import PetAdoption
from .serializers import PetAdoptionListSerializer, PetAdoptionDetailSerializer
from rest_framework.permissions import IsAdminUser
from rest_framework.permissions import AllowAny, IsAuthenticated

from rest_framework import permissions

class IsAdminOrOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Admin can do anything
        if request.user.is_staff:
            return True
        # Owner can delete their own pet
        return obj.user == request.user
        
class PetAdoptionView(ModelViewSet):
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return PetAdoptionDetailSerializer
        return PetAdoptionListSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return PetAdoption.objects.all()
        return PetAdoption.objects.filter(is_approved=True)

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated()]
        elif self.action in ['update', 'partial_update']:
            return [IsAdminUser()]  # only admin can approve/edit
        elif self.action == 'destroy':
            return [IsAuthenticated(), IsAdminOrOwner()]  # admin or owner can delete
        return [AllowAny()]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, is_approved=False)