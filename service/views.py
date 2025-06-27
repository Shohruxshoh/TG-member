from rest_framework import viewsets, permissions
from .models import Country, ServicePrice, Link
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter

from .serializers import CountrySerializer, ServicePriceSerializer, LinkSerializer, LinkCreateSerializer


class CountryViewSet(viewsets.ModelViewSet):
    queryset = Country.objects.all().order_by('name')
    serializer_class = CountrySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class ServicePriceViewSet(viewsets.ModelViewSet):
    queryset = ServicePrice.objects.all().order_by('-created_at')
    serializer_class = ServicePriceSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['country', 'category']
    search_fields = ['category']


class LinkViewSet(viewsets.ModelViewSet):
    queryset = Link.objects.all().order_by('-created_at')
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return LinkCreateSerializer
        return LinkSerializer

    def perform_create(self, serializer):
        serializer.save()
