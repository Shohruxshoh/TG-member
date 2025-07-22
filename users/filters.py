import django_filters
from  users.models import User, TelegramAccount

class AUserFilter(django_filters.FilterSet):
    date_joined_after = django_filters.DateFilter(field_name='date_joined', lookup_expr='gte')
    date_joined_before = django_filters.DateFilter(field_name='date_joined', lookup_expr='lte')

    class Meta:
        model = User
        fields = ['date_joined_after', 'date_joined_before', 'is_active']


class ATelegramAccountFilter(django_filters.FilterSet):
    created_at_after = django_filters.DateFilter(field_name='created_at', lookup_expr='gte')
    created_at_before = django_filters.DateFilter(field_name='created_at', lookup_expr='lte')

    class Meta:
        model = TelegramAccount
        fields = ['created_at_after', 'created_at_before', 'is_active']

