from django_filters import rest_framework as filters
from order.models import Order


class OrderFilter(filters.FilterSet):
    created_at = filters.DateFromToRangeFilter()

    class Meta:
        model = Order
        fields = ['status', 'service', 'service__category', 'created_at']


class OrderLinkFilter(filters.FilterSet):
    class Meta:
        model = Order
        fields = ['service__category']
