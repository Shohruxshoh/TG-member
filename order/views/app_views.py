from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework import permissions, generics, status
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.response import Response
from order.models import Order
from order.permissions import IsOwnerOrReadOnly
from order.serializers.app_serializers import SOrderSerializer, SOrderDetailSerializer, SOrderLinkCreateSerializer, \
    STelegramBackfillSerializer
from order.filters import OrderFilter
from order.services import save_links_for_order
from order.telegram_fetch import fetch_prior_message_urls
from service.models import Link, Service
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from asgiref.sync import async_to_sync
from service.schemas import COMMON_RESPONSES


@extend_schema(
    responses={
        200: OpenApiResponse(
            response=SOrderSerializer
        ),
        **COMMON_RESPONSES
    }
)
class SOrderListAPIViews(generics.ListAPIView):
    queryset = Order.objects.select_related('service', 'user', 'parent').all()
    serializer_class = SOrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    # 🔽 Filter va qidiruv sozlamalari
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = OrderFilter
    search_fields = ['status', 'service__category']  # qidiruv uchun
    ordering_fields = ['created_at', 'price']  # tartiblash
    ordering = ['-created_at']  # default ordering

    def get_queryset(self):
        # Foydalanuvchi faqat o‘z buyurtmalarini ko‘radi
        return Order.objects.select_related('service', 'user', 'parent').filter(user=self.request.user, is_active=True,
                                                                                parent__isnull=True)


@extend_schema(
    responses={
        200: OpenApiResponse(
            response=SOrderSerializer
        ),
        **COMMON_RESPONSES
    }
)
class SOrderDetailAPIView(generics.RetrieveAPIView):
    queryset = Order.objects.select_related('service', 'user', 'parent').filter(is_active=True)
    serializer_class = SOrderDetailSerializer
    permission_classes = [IsOwnerOrReadOnly]


@extend_schema(
    request=SOrderLinkCreateSerializer,
    responses={
        201: {
            'type': 'object',
            'properties': {
                'order_id': {'type': 'integer'},
                'link': {'type': 'string'},
                'channel_name': {'type': 'string'},
            }
        },
        **COMMON_RESPONSES
    },
)
class SOrderLinkCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = SOrderLinkCreateSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        return Response(result, status=status.HTTP_201_CREATED)


class STelegramBackfillAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        request=STelegramBackfillSerializer,
        responses={
            200: {
                'type': 'object',
                'properties': {
                    "requested": {'type': 'integer'},
                    "fetched_from_telegram": {'type': 'integer'},
                    "saved_to_db": {'type': 'integer'},
                    "already_in_db": {'type': 'integer'},
                }
            },
            **COMMON_RESPONSES
        },
    )
    def post(self, request, *args, **kwargs):
        serializer = STelegramBackfillSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service_id = serializer.validated_data["service_id"]
        url = serializer.validated_data["url"]
        count = serializer.validated_data["count"]

        service = get_object_or_404(Service, pk=service_id)

        # Async Telegramdan URL’larni yig‘amiz
        try:
            urls = async_to_sync(fetch_prior_message_urls)(url, count)
        except Exception as e:
            return Response({"detail": f"Telegramdan olishda xatolik: {e}"}, status=status.HTTP_400_BAD_REQUEST)
        # Sync DB yozuvlari
        save_result = save_links_for_order(service, request.user, urls)

        return Response({
            "requested": count,
            "fetched_from_telegram": len(urls),
            "saved_to_db": save_result["created"],
            "already_in_db": save_result["existing"],
        }, status=status.HTTP_200_OK)

# class SOrderWithLinksChildCreateAPIView(APIView):
#     permission_classes = [permissions.IsAuthenticated]
#
#     @extend_schema(
#         request=SOrderWithLinksChildCreateSerializer,
#         responses={
#             201: {
#                 'type': 'object',
#                 'properties': {
#                     'order_id': {'type': 'integer'},
#                     'links': {'type': 'array', 'items': {'type': 'string'}}
#                 }
#             }
#         },
#         description="Yangi Order yaratadi va unga bir nechta Link larni bir vaqtda bog‘laydi"
#     )
#     def post(self, request):
#         serializer = SOrderWithLinksChildCreateSerializer(data=request.data, context={'request': request})
#         serializer.is_valid(raise_exception=True)
#         result = serializer.save()
#         return Response(result, status=status.HTTP_201_CREATED)
