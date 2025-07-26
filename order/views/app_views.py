from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter
from rest_framework import permissions, generics, status
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.response import Response
from order.models import Order, OrderMember
from order.permissions import IsOwnerOrReadOnly
from order.serializers.app_serializers import SOrderSerializer, SOrderDetailSerializer, SOrderLinkCreateSerializer, \
    STelegramBackfillSerializer, SAddVipSerializer, SOrderLinkListSerializer
from order.filters import OrderFilter, OrderLinkFilter
from order.services import save_links_for_order
from order.telegram_fetch import fetch_prior_message_urls
from service.models import Service
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from asgiref.sync import async_to_sync
from service.schemas import COMMON_RESPONSES
from django.utils.timezone import now
from datetime import timedelta
from django.db.models import OuterRef, Subquery, Exists
from django.db.models.functions import Now


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
            response=SOrderDetailSerializer
        ),
        **COMMON_RESPONSES
    }
)
class SOrderDetailAPIView(generics.RetrieveAPIView):
    queryset = Order.objects.select_related('service', 'user', 'parent').filter(is_active=True)
    serializer_class = SOrderDetailSerializer
    permission_classes = [IsOwnerOrReadOnly]


@extend_schema(
    parameters=[
        OpenApiParameter("telegram_id", str, OpenApiParameter.QUERY, required=True)
    ],
    responses={
        200: OpenApiResponse(
            response=SOrderLinkListSerializer
        ),
        **COMMON_RESPONSES
    }
)
class SOrderLinkListAPIView(generics.ListAPIView):
    serializer_class = SOrderLinkListSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = OrderLinkFilter
    search_fields = ['link', 'channel_name']

    def get_queryset(self):
        user = self.request.user
        telegram_id = self.request.query_params.get('telegram_id')
        if not telegram_id:
            return Order.objects.none()  # Telegram ID bo'lmasa, hech narsa qaytarmaymiz

        three_days_ago = now() - timedelta(days=3)

        # Subquery: Shu foydalanuvchi va telegram_id bilan OrderMember mavjudmi?
        recent_member_qs = OrderMember.objects.filter(
            order=OuterRef('pk'),
            user=user,
            telegram__telegram_id=telegram_id,
            joined_at__gt=three_days_ago
        )

        any_member_qs = OrderMember.objects.filter(
            order=OuterRef('pk'),
            user=user,
            telegram__telegram_id=telegram_id
        )

        return (
            Order.objects
            .select_related('service', 'user', 'parent')
            .filter(is_active=True, status="PROCESSING")
            .annotate(
                has_recent_member=Exists(recent_member_qs),
                has_any_member=Exists(any_member_qs)
            )
            .filter(
                has_recent_member=False  # 3 kundan yangi bo‘lsa — SKIP
            )
        )


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


@extend_schema(
    request=SAddVipSerializer,
    responses={
        # 201: SAddVipSerializer,
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
class SAddVipAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = SAddVipSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "success"}, status=status.HTTP_201_CREATED)

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
