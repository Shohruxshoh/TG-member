from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample
from rest_framework import status
from rest_framework.generics import ListCreateAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from balance.models import Balance, Transfer, Buy, OrderBuy, GiftUsage
from balance.serializers.app_serializers import SBalanceUpdateSerializer, SBalanceSerializer, STransferSerializer, \
    SGiftActivateSerializer, SBuySerializers, SOrderBuySerializers, SGiftUsageSerializer
from django_filters.rest_framework import DjangoFilterBackend


# Create your views here.

# Balance

@extend_schema(
    summary="Balansga qiymat qo‘shish.",
    description="""
                Foydalanuvchining balansiga qiymat qo‘shish  uchun API.            
                **Masalan:**  
                `amount`: 10000 → balansga qo‘shadi  
                """,
    request=SBalanceUpdateSerializer,
    responses={
        200: OpenApiResponse(
            response=SBalanceSerializer,
            description="Balans muvaffaqiyatli yangilandi. `balance` — yangilangan qiymat."
        ),
        400: OpenApiResponse(description="Xatolik: balans manfiy bo'lishi mumkin emas yoki noto‘g‘ri qiymat."),
        404: OpenApiResponse(description="Balans topilmadi."),
        401: OpenApiResponse(description="Avtorizatsiya talab qilinadi."),
    },
    tags=["Balans"]
)
class SBalanceAddUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        serializer = SBalanceUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            balance = Balance.objects.get(user=request.user)
            new_balance = balance.perform_balance_update(serializer.validated_data["amount"])
            return Response({"detail": "Balans yangilandi", "balance": new_balance}, status=status.HTTP_200_OK)
        except Balance.DoesNotExist:
            return Response({"detail": "Balans topilmadi"}, status=status.HTTP_404_NOT_FOUND)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary="Balansdan qiymat ayirish",
    description="""
                Foydalanuvchining balansidan coin ayirish uchun API.

                **Masalan:**  
                `amount`: 5000 → balansdan ayiradi
                """,
    request=SBalanceUpdateSerializer,
    responses={
        200: OpenApiResponse(
            response=SBalanceSerializer,
            description="Balans muvaffaqiyatli yangilandi. `balance` — yangilangan qiymat."
        ),
        400: OpenApiResponse(description="Xatolik: balans manfiy bo'lishi mumkin emas yoki noto‘g‘ri qiymat."),
        404: OpenApiResponse(description="Balans topilmadi."),
        401: OpenApiResponse(description="Avtorizatsiya talab qilinadi."),
    },
    tags=["Balans"]
)
class SBalanceSubtractionUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        serializer = SBalanceUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            balance = Balance.objects.get(user=request.user)
            new_balance = balance.perform_balance_subtraction_update(serializer.validated_data["amount"])
            return Response({"detail": "Balans yangilandi", "balance": new_balance}, status=status.HTTP_200_OK)
        except Balance.DoesNotExist:
            return Response({"detail": "Balans topilmadi"}, status=status.HTTP_404_NOT_FOUND)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary="Foydalanuvchining balansini olish",
    description="Tizimga kirgan foydalanuvchining balansini olish uchun API. Faqat autentifikatsiyadan o‘tgan foydalanuvchi o‘z balansini ko‘ra oladi.",
    responses={
        200: SBalanceSerializer,
        404: {"description": "Balans topilmadi"},
        401: {"description": "Avtorizatsiya talab qilinadi"},
    },
    tags=["Balans"]
)
class SBalanceMeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            balance = Balance.objects.select_related('user').get(user=request.user)
        except Balance.DoesNotExist:
            return Response({"detail": "Balans topilmadi."}, status=status.HTTP_404_NOT_FOUND)

        serializer = SBalanceSerializer(balance)
        return Response(serializer.data, status=status.HTTP_200_OK)


class STransferListCreateAPIView(ListCreateAPIView):
    serializer_class = STransferSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Transfer.objects.select_related('sender').filter(sender=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save()


@extend_schema(
    request=SGiftActivateSerializer,
    responses={
        200: OpenApiResponse(
            response=None,
            description="Gift kodi muvaffaqiyatli aktivlashtirildi",
            examples=[
                OpenApiExample(
                    "Muvaffaqiyatli",
                    value={
                        "detail": "Gift muvaffaqiyatli aktivlashtirildi.",
                        "gift": "ABC123XYZ",
                        "value": 500
                    }
                )
            ]
        ),
        400: OpenApiResponse(
            description="Xatolik yuz berdi",
            examples=[
                OpenApiExample(
                    "Xatolik",
                    value={"gift": ["Bunday gift kodi mavjud emas."]}
                )
            ]
        )
    },
    tags=["Gift"]
)
class SGiftActivateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = SGiftActivateSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        gift = serializer.save()
        return Response({
            "detail": "Gift muvaffaqiyatli aktivlashtirildi.",
            "gift": gift.gift,
            "value": gift.value
        }, status=status.HTTP_200_OK)


class SGiftUsageAPIView(ListAPIView):
    serializer_class = SGiftUsageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return GiftUsage.objects.select_related('user', 'gift').filter(user=self.request.user).order_by('-used_at')


class SBuyListAPIView(ListAPIView):
    queryset = Buy.objects.filter(is_active=True).order_by('coin', 'price')
    serializer_class = SBuySerializers
    permission_classes = [IsAuthenticated]


class SOrderBuyListAPIView(ListAPIView):
    queryset = OrderBuy.objects.all()
    serializer_class = SOrderBuySerializers
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_paid']

    def get_queryset(self):
        return OrderBuy.objects.select_related('user', 'buy').filter(user=self.request.user).order_by('-created_at')
