from django.shortcuts import render
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from balance.models import Balance
from balance.serializers import BalanceUpdateSerializer, BalanceSerializer


# Create your views here.

# Balance

@extend_schema(
    summary="Balansga qiymat qo‘shish.",
    description="""
                Foydalanuvchining balansiga qiymat qo‘shish  uchun API.            
                **Masalan:**  
                `amount`: 10000 → balansga qo‘shadi  
                """,
    request=BalanceUpdateSerializer,
    responses={
        200: OpenApiResponse(
            response=BalanceSerializer,
            description="Balans muvaffaqiyatli yangilandi. `balance` — yangilangan qiymat."
        ),
        400: OpenApiResponse(description="Xatolik: balans manfiy bo'lishi mumkin emas yoki noto‘g‘ri qiymat."),
        404: OpenApiResponse(description="Balans topilmadi."),
        401: OpenApiResponse(description="Avtorizatsiya talab qilinadi."),
    },
    tags=["Balans"]
)
class BalanceAddUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        serializer = BalanceUpdateSerializer(data=request.data)
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
    request=BalanceUpdateSerializer,
    responses={
        200: OpenApiResponse(
            response=BalanceSerializer,
            description="Balans muvaffaqiyatli yangilandi. `balance` — yangilangan qiymat."
        ),
        400: OpenApiResponse(description="Xatolik: balans manfiy bo'lishi mumkin emas yoki noto‘g‘ri qiymat."),
        404: OpenApiResponse(description="Balans topilmadi."),
        401: OpenApiResponse(description="Avtorizatsiya talab qilinadi."),
    },
    tags=["Balans"]
)
class BalanceSubtractionUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        serializer = BalanceUpdateSerializer(data=request.data)
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
        200: BalanceSerializer,
        404: {"description": "Balans topilmadi"},
        401: {"description": "Avtorizatsiya talab qilinadi"},
    },
    tags=["Balans"]
)
class BalanceMeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            balance = Balance.objects.select_related('user').get(user=request.user)
        except Balance.DoesNotExist:
            return Response({"detail": "Balans topilmadi."}, status=status.HTTP_404_NOT_FOUND)

        serializer = BalanceSerializer(balance)
        return Response(serializer.data, status=status.HTTP_200_OK)
