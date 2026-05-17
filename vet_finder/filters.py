# filters.py
from django_filters import rest_framework as filters
from .models import Hospital

class HospitalFilter(filters.FilterSet):
    tags = filters.BaseInFilter(field_name='tags__name', lookup_expr='in')
    services = filters.BaseInFilter(field_name='services__name', lookup_expr='in')

    class Meta:
        model = Hospital
        fields = ['tags', 'services']