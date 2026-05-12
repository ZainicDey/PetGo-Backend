from django.urls import path
from .views import (
    TagListCreateView,
    TagDetailView,
    HouseListCreateView,
    HouseDetailView,
)

urlpatterns = [
    path('foster-house-finder/tags/', TagListCreateView.as_view(), name='tag-list-create'),
    path('foster-house-finder/tags/<int:pk>/', TagDetailView.as_view(), name='tag-detail'),
    path('foster-house-finder/houses/', HouseListCreateView.as_view(), name='house-list-create'),
    path('foster-house-finder/houses/<int:pk>/', HouseDetailView.as_view(), name='house-detail'),
]