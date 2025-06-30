from django.shortcuts import render
from .serializers import RegisterSerializer, RegisterGoogleSerializer, LoginGoogleSerializer, PasswordChangeSerializer, \
    PasswordResetEmailRequestSerializer, PasswordResetConfirmSerializer, BalanceUpdateSerializer, BalanceSerializer, \
    UserSerializer
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import User, Balance
from rest_framework.permissions import AllowAny, IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse
from django.views import View
from django.http import JsonResponse


# Create your views here.

class RegisterView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


class RegisterGoogleView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterGoogleSerializer
    permission_classes = [AllowAny]


class LoginGoogleView(APIView):
    @extend_schema(
        request=LoginGoogleSerializer,
        responses={
            200: OpenApiExample(
                name="Login successful",
                value={
                    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOi...",
                    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOi...",
                },
                response_only=True,
            ),
            400: OpenApiExample(
                name="Login error",
                value={"non_field_errors": ["Bunday foydalanuvchi mavjud emas."]},
                response_only=True,
            ),
        },
        description="Foydalanuvchi Google orqali email orqali tizimga kiradi. JWT token qaytariladi.",
    )
    def post(self, request, *args, **kwargs):
        serializer = LoginGoogleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class PasswordChangeView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=PasswordChangeSerializer,
        responses={
            200: OpenApiResponse(response=PasswordChangeSerializer, description="Parol muvaffaqiyatli o'zgartirildi."),
            400: OpenApiResponse(description="Parolni o'zgartirishda xatolik."),
        },
        description="Foydalanuvchi yangi parolni kiritib, mavjud parolini yangilaydi. Parollar mos bo'lishi kerak.",
    )
    def patch(self, request, *args, **kwargs):
        serializer = PasswordChangeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        user.set_password(serializer.validated_data['password1'])
        user.save()

        return Response({"message": "success"}, status=status.HTTP_200_OK)


class PasswordResetEmailView(APIView):
    @extend_schema(
        request=PasswordResetEmailRequestSerializer,
        responses={200: {"description": "Tiklash havolasi yuborildi"}}
    )
    def post(self, request):
        serializer = PasswordResetEmailRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(request)
        return Response({"message": "Parolni tiklash havolasi emailingizga yuborildi"}, status=status.HTTP_200_OK)


# class PasswordResetConfirmView(APIView):
#     @extend_schema(
#         request=PasswordResetConfirmSerializer,
#         responses={200: {"description": "Parol muvaffaqiyatli o‘zgartirildi"}}
#     )
#     def post(self, request, uidb64, token):
#         data = {
#             "uidb64": uidb64,
#             "token": token,
#             "password1": request.data.get("password1"),
#             "password2": request.data.get("password2"),
#         }
#         serializer = PasswordResetConfirmSerializer(data=data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response({"message": "Parol muvaffaqiyatli o‘zgartirildi"}, status=status.HTTP_200_OK)


class PasswordResetConfirmTemplateView(View):
    def get(self, request, uidb64, token):
        return render(request, 'reset_password_confirm.html', {
            'uidb64': uidb64,
            'token': token
        })

    def post(self, request, uidb64, token):
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        data = {
            "uidb64": uidb64,
            "token": token,
            "password1": password1,
            "password2": password2,
        }

        serializer = PasswordResetConfirmSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse({"message": "Parol muvaffaqiyatli o‘zgartirildi"}, status=status.HTTP_200_OK)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary="Foydalanuvchining malumotlarini olish",
    description="Tizimga kirgan foydalanuvchining balansini va malumotlarini olish uchun API.\
     Faqat autentifikatsiyadan o‘tgan foydalanuvchi o‘z balansini ko‘ra oladi.",
    responses={
        200: UserSerializer,
        404: {"description": "Foydalanuvchi topilmadi"},
        401: {"description": "Avtorizatsiya talab qilinadi"},
    },
    tags=["User"]
)
class UserMeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user = User.objects.get(id=self.request.user.id)
        except User.DoesNotExist:
            return Response({"detail": "User topilmadi."}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


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
