# filters.py
from django_filters import rest_framework as filters
from django.utils import timezone
from datetime import timedelta
from .models import Link


class LinkFilter(filters.FilterSet):
    order = filters.NumberFilter(field_name='order')
    service_category = filters.CharFilter(field_name='order__service_category')
    country_code = filters.CharFilter(field_name='order__service__country__country_code')

    class Meta:
        model = Link
        fields = ['order', 'service_category', 'country_code']
