from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema
from .models import Country, ServicePrice, Link
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter

from .serializers import CountrySerializer, ServicePriceSerializer, LinkSerializer, OrderWithLinksCreateSerializer


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
    serializer_class = LinkSerializer

    def perform_create(self, serializer):
        serializer.save()


class OrderWithLinksCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        request=OrderWithLinksCreateSerializer,
        responses={
            201: {
                'type': 'object',
                'properties': {
                    'order_id': {'type': 'integer'},
                    'links': {'type': 'array', 'items': {'type': 'string'}}
                }
            }
        },
        description="Yangi Order yaratadi va unga bir nechta Link larni bir vaqtda bog‘laydi"
    )
    def post(self, request):
        serializer = OrderWithLinksCreateSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        return Response(result)

