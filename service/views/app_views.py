from rest_framework import permissions, generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from service.models import Country, Service
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from service.schemas import COMMON_RESPONSES
from service.serializers.app_serializers import SCountrySerializer, SServiceSerializer, \
    SOrderWithLinksCreateSerializer
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from drf_spectacular.utils import extend_schema, OpenApiResponse


@extend_schema(
    responses={
        200: OpenApiResponse(
            response=SCountrySerializer
        ),
        **COMMON_RESPONSES
    }
)
@method_decorator(cache_page(60 * 5, key_prefix="cache_country"), name='dispatch')  # 5 daqiqaga cache
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
@method_decorator(cache_page(60 * 5, key_prefix="cache_service"), name='dispatch')  # 5 daqiqaga cache
class SServiceListAPIView(generics.ListAPIView):
    queryset = Service.objects.select_related('country').filter(is_active=True).order_by('-created_at')
    serializer_class = SServiceSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['country', 'category', 'post']
    search_fields = ['category']


# @extend_schema(
#     parameters=[
#         OpenApiParameter("telegram_id", str, OpenApiParameter.QUERY, required=True)
#     ],
#     responses={
#         200: OpenApiResponse(
#             response=SLinkSerializer
#         ),
#         **COMMON_RESPONSES
#     }
# )
# class SLinkListAPIView(generics.ListAPIView):
#     serializer_class = SLinkSerializer
#     permission_classes = [permissions.IsAuthenticated]
#     filter_backends = [DjangoFilterBackend, SearchFilter]
#     filterset_class = LinkFilter
#     search_fields = ['link', 'channel_name']
#
#     def get_queryset(self):
#         user = self.request.user
#         telegram_id = self.request.query_params.get("telegram_id")
#
#         if not telegram_id:
#             return Link.objects.none()  # yoki raise ValidationError("telegram_id kerak")
#
#         three_days_ago = timezone.now() - timedelta(days=3)
#
#         ordermember_qs = OrderMember.objects.filter(
#             order=OuterRef('order_id'),
#             user=user,
#             telegram_id=telegram_id
#         ).order_by('-joined_at')
#
#         links = Link.objects.select_related('order').annotate(
#             member_joined_at=Subquery(ordermember_qs.values('joined_at')[:1], output_field=DateTimeField())
#         ).filter(
#             order__is_active=True,
#             order__status="PROCESSING"
#         ).filter(
#             Q(member_joined_at__isnull=True) |
#             Q(member_joined_at__lt=three_days_ago)
#         )
#         return links


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
