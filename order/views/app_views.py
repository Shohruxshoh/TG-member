from django.db.models.functions import Coalesce
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter, OpenApiExample
from rest_framework import permissions, generics, status
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.response import Response
# from silk.profiling.profiler import silk_profile
from order.enums import Status
from order.models import Order, OrderMember
# from order.utils import explain_analyze
from users.models import TelegramAccount
from order.permissions import IsOwnerOrReadOnly
from order.serializers.app_serializers import SOrderSerializer, SOrderDetailSerializer, SOrderLinkCreateSerializer, \
    STelegramBackfillSerializer, SAddVipSerializer, SOrderLinkListSerializer, SCheckAddedChannelSerializer, \
    TelegramListSerializer
from order.filters import OrderFilter, OrderLinkFilter
from order.services import save_links_for_order
from order.telegram_fetch import fetch_prior_message_urls
from service.models import Service
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from collections import defaultdict
from asgiref.sync import async_to_sync
from service.schemas import COMMON_RESPONSES
from django.utils.timezone import now
from datetime import timedelta
from django.db.models import F, OuterRef, Subquery, Exists, Count, Q, IntegerField


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
        OpenApiParameter(
            name="telegram_id",
            type=str,
            location=OpenApiParameter.QUERY,
            required=True,
            many=True,
            style='form',
            explode=True,
            description="Telegram ID lar ro'yxati (?telegram_id=123&telegram_id=456)"
        )
    ],
    responses={
        200: OpenApiResponse(response=SOrderLinkListSerializer),
        **COMMON_RESPONSES
    }
)
class SOrderLinkListAPIView(generics.ListAPIView):
    serializer_class = SOrderLinkListSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]  # , SearchFilter
    filterset_class = OrderLinkFilter

    # search_fields = ['link', 'channel_name']

    # @silk_profile()
    def get_queryset(self):
        user = self.request.user
        telegram_ids = self.request.query_params.getlist('telegram_id')
        # telegram_ids = [int(tid) for tid in telegram_ids if tid.isdigit()]

        if not telegram_ids:
            return Order.objects.none()

        telegram_accounts_qs = TelegramAccount.objects.select_related('user').filter(
            telegram_id__in=telegram_ids,
            is_active=True
        ).values_list("id", flat=True)
        # telegram_account_ids = list(telegram_accounts_qs.values_list('id', flat=True))

        # country_codes = list(telegram_accounts_qs.values_list('country_code', flat=True))

        if not telegram_accounts_qs:
            return Order.objects.none()

        three_days_ago = now() - timedelta(days=3)

        base_orders_qs = (
            Order.objects
            .select_related('parent')  # Only select parent relation as we need minimal fields
            .filter(
                is_active=True,
                status=Status.PROCESSING,
                # country_code__in=country_codes
            )
            .only('id', 'link', 'channel_name', 'channel_id', 'parent_id')  # Only fields we actually need
        )

        orders_with_recent_member_count = base_orders_qs.prefetch_related('members').annotate(
            recent_member_count=Count(
                'members',
                filter=(
                        Q(members__user=user) &
                        Q(members__telegram_id__in=telegram_accounts_qs) &
                        Q(members__joined_at__gt=three_days_ago)
                )
            )
        )

        return (
            orders_with_recent_member_count
            .filter(recent_member_count__lt=len(telegram_ids))
            .distinct()
            .values('id', 'link', 'channel_name', 'channel_id')  # country_code
        )
    # def get_queryset(self):
    #     user = self.request.user
    #     telegram_ids = self.request.query_params.getlist('telegram_id', [])
    #
    #     # 1. Boshlang'ich tekshiruvlar
    #     if not telegram_ids:
    #         return Order.objects.none()
    #
    #     # 2. Telegram akkauntlarini oldindan yuklash
    #     telegram_account_ids = list(
    #         TelegramAccount.objects.filter(
    #             telegram_id__in=telegram_ids,
    #             is_active=True
    #         ).values_list('id', flat=True)
    #     )
    #
    #     if not telegram_account_ids:
    #         return Order.objects.none()
    #
    #     three_days_ago = now() - timedelta(days=3)
    #
    #     # 3. Optimallashtirilgan subquery yaratish
    #     recent_members_subquery = (
    #         OrderMember.objects.filter(
    #             order_id=OuterRef('pk'),
    #             user=user,
    #             telegram_id__in=telegram_account_ids,
    #             joined_at__gt=three_days_ago
    #         )
    #         .values('order_id')
    #         .annotate(count=Count('id'))
    #         .values('count')
    #     )
    #
    #     # 4. Asosiy optimallashtirilgan so'rov
    #     optimized_qs = (
    #         Order.objects
    #         .filter(
    #             is_active=True,
    #             status=Status.PROCESSING
    #         )
    #         .annotate(
    #             recent_member_count=Coalesce(
    #                 Subquery(recent_members_subquery),
    #                 0,
    #                 output_field=IntegerField()
    #             )
    #         )
    #         .filter(recent_member_count__lt=len(telegram_ids))
    #         .select_related('parent')
    #         .only('id', 'link', 'channel_name', 'channel_id', 'parent_id')
    #         .distinct()
    #     )
    #
    #     return optimized_qs.values('id', 'link', 'channel_name', 'channel_id')


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
        serializer = STelegramBackfillSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        service_id = serializer.validated_data["service_id"]
        url = serializer.validated_data["url"]
        count = serializer.validated_data["count"]
        channel_name = serializer.validated_data["channel_name"]
        channel_id = serializer.validated_data["channel_id"]

        service = get_object_or_404(Service, pk=service_id)

        # Async Telegramdan URL’larni yig‘amiz
        try:
            urls = async_to_sync(fetch_prior_message_urls)(url, count)
        except Exception as e:
            return Response({"detail": f"Telegramdan olishda xatolik: {e}"}, status=status.HTTP_400_BAD_REQUEST)
        # Sync DB yozuvlari
        save_result = save_links_for_order(service, request.user, urls, channel_name, channel_id)

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
                'telegram_id': {'type': 'string'},
                'created_at': {'type': 'string'},
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
        created_members = serializer.save()
        results = [
            {
                "order_id": m.order.id,
                "channel_name": m.order.channel_name,
                "link": m.order.link,
                "telegram_id": m.telegram.telegram_id,
                "created_at": m.joined_at,
            }
            for m in created_members
        ]
        return Response({"results": results}, status=status.HTTP_201_CREATED)


class SCheckAddedChannelAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        request=SCheckAddedChannelSerializer,
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'message': {'type': 'boolean'},
                }
            },
            **COMMON_RESPONSES
        },
        description="""Returns false if the user is subscribed, true otherwise."""
    )
    def post(self, request, *args, **kwargs):
        serializer = SCheckAddedChannelSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        is_recent_member = serializer.validated_data['is_recent_member']
        return Response({"message": not is_recent_member}, status=status.HTTP_200_OK)


@extend_schema(
    summary="Foydalanuvchi Telegram accountlariga tegishli channel_id va order_id ro'yxati",
    description=(
            "Login qilgan foydalanuvchining barcha Telegram accountlarini tekshiradi "
            "va ularga ulangan Orderlardan channel_id va order_id'larni qaytaradi."
    ),
    responses={
        200: {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "telegram_id": {"type": "string", "example": "11111111"},
                    "channels": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "order_id": {"type": "integer", "example": 1},
                                "channel_id": {"type": "string", "example": "123"}
                            }
                        }
                    }
                }
            }
        }
    },
    examples=[
        OpenApiExample(
            name="Oddiy javob",
            value=[
                {
                    "telegram_id": "11111111",
                    "channels": [
                        {"order_id": 1, "channel_id": "123"},
                        {"order_id": 2, "channel_id": "456"}
                    ]
                },
                {
                    "telegram_id": "22222222",
                    "channels": [
                        {"order_id": 3, "channel_id": "789"}
                    ]
                }
            ]
        )
    ]
)
class UserTelegramChannelsView(APIView):
    """
    Login bo'lgan foydalanuvchining telegram accountlariga
    tegishli bo'lgan barcha order_id va channel_id'larni qaytaradi.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user

        qs = (
            OrderMember.objects
            .filter(telegram__user=user, user=user, is_active=True)
            .select_related('order', 'telegram', 'user')
            .values('telegram__telegram_id', 'order__id', 'order__channel_id')
            .distinct()
        )

        grouped_data = defaultdict(list)
        for row in qs:
            grouped_data[row['telegram__telegram_id']].append({
                "order_id": row['order__id'],
                "channel_id": row['order__channel_id']
            })

        response_data = [
            {
                "telegram_id": telegram_id,
                "channels": channels
            }
            for telegram_id, channels in grouped_data.items()
        ]

        return Response(response_data)


class TelegramCheckListAPIView(APIView):
    """
    Frontenddan kelgan telegram_id + order_id larni tekshiradi va
    muddati o'tganlarni is_active=False qiladi.
    """
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        request=TelegramListSerializer,
        responses={
            200: OpenApiExample(
                "Muvaffaqiyatli javob",
                value={"message": "Tekshiruv yakunlandi, kerakli o'zgarishlar kiritildi."}
            ),
            **COMMON_RESPONSES
        },
        examples=[
            OpenApiExample(
                "So‘rov namunasi",
                value=[
                    {
                        "telegram_id": "12345",
                        "channels": [
                            {"order_id": 1, "channel_id": "1"},
                            {"order_id": 34, "channel_id": "string"},
                            {"order_id": 37, "channel_id": "777777"}
                        ]
                    },
                    {
                        "telegram_id": "123456",
                        "channels": [
                            {"order_id": 1, "channel_id": "1"},
                            {"order_id": 37, "channel_id": "777777"}
                        ]
                    }
                ],
                request_only=True
            )
        ]
    )
    def post(self, request):
        serializer = TelegramListSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        return Response(
            {"message": "Tekshiruv yakunlandi, kerakli o'zgarishlar kiritildi."},
            status=status.HTTP_200_OK
        )

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
