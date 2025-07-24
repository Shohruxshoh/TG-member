from rest_framework import permissions, generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiResponse
from service.models import Country, Service, Link
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter

from service.schemas import COMMON_RESPONSES
from service.serializers.app_serializers import SCountrySerializer, SServiceSerializer, SLinkSerializer, \
    SOrderWithLinksCreateSerializer


@extend_schema(
    responses={
        200: OpenApiResponse(
            response=SCountrySerializer
        ),
        **COMMON_RESPONSES
    }
)
class SCountryListAPIView(generics.ListAPIView):
    queryset = Country.objects.filter(is_active=True).order_by('name')
    serializer_class = SCountrySerializer
    permission_classes = [permissions.IsAuthenticated]


@extend_schema(
    responses={
        200: OpenApiResponse(
            response=SServiceSerializer
        ),
        **COMMON_RESPONSES
    }
)
class SServiceListAPIView(generics.ListAPIView):
    queryset = Service.objects.select_related('country').filter(is_active=True).order_by('-created_at')
    serializer_class = SServiceSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['country', 'category', 'post']
    search_fields = ['category']


@extend_schema(
    responses={
        200: OpenApiResponse(
            response=SLinkSerializer
        ),
        **COMMON_RESPONSES
    }
)
class SLinkListAPIView(generics.ListAPIView):
    queryset = Link.objects.select_related('order').filter(order__is_active=True, order__status="PROCESSING")
    serializer_class = SLinkSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['order', 'order__service_category']
    search_fields = ['link', 'channel_name']


class SOrderWithLinksCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        request=SOrderWithLinksCreateSerializer,
        responses={
            201: {
                'type': 'object',
                'properties': {
                    'order_id': {'type': 'integer'},
                    'links': {'type': 'array', 'items': {'type': 'string'}}
                }
            },
            **COMMON_RESPONSES
        },
        description="Yangi Order yaratadi va unga bir nechta Link larni bir vaqtda bog‘laydi"
    )
    def post(self, request):
        serializer = SOrderWithLinksCreateSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        return Response(result, status=status.HTTP_201_CREATED)
