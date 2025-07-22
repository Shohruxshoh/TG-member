from django.shortcuts import render
from rest_framework.generics import CreateAPIView, ListCreateAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from users.models import User, TelegramAccount
from rest_framework.permissions import AllowAny, IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse
from django.views import View
from django.http import JsonResponse
from users.serializers.app_serializers import SRegisterSerializer, SRegisterGoogleSerializer, SLoginGoogleSerializer, \
    SPasswordChangeSerializer, SPasswordResetEmailRequestSerializer, SPasswordResetConfirmSerializer, SUserSerializer, \
    SUserChangeEmailSerializer, STelegramAccountSerializer


# Create your views here.

class SRegisterView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = SRegisterSerializer
    permission_classes = [AllowAny]


class SRegisterGoogleView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = SRegisterGoogleSerializer
    permission_classes = [AllowAny]


class SLoginGoogleView(APIView):
    @extend_schema(
        request=SLoginGoogleSerializer,
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
        serializer = SLoginGoogleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class SPasswordChangeView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=SPasswordChangeSerializer,
        responses={
            200: OpenApiResponse(response=SPasswordChangeSerializer, description="Parol muvaffaqiyatli o'zgartirildi."),
            400: OpenApiResponse(description="Parolni o'zgartirishda xatolik."),
        },
        description="Foydalanuvchi yangi parolni kiritib, mavjud parolini yangilaydi. Parollar mos bo'lishi kerak.",
    )
    def patch(self, request, *args, **kwargs):
        serializer = SPasswordChangeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        user.set_password(serializer.validated_data['password1'])
        user.save()

        return Response({"message": "success"}, status=status.HTTP_200_OK)


class SPasswordResetEmailView(APIView):
    @extend_schema(
        request=SPasswordResetEmailRequestSerializer,
        responses={200: {"description": "Tiklash havolasi yuborildi"}}
    )
    def post(self, request):
        serializer = SPasswordResetEmailRequestSerializer(data=request.data)
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


class SPasswordResetConfirmTemplateView(View):
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

        serializer = SPasswordResetConfirmSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse({"message": "Parol muvaffaqiyatli o‘zgartirildi"}, status=status.HTTP_200_OK)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary="Foydalanuvchining malumotlarini olish",
    description="Tizimga kirgan foydalanuvchining balansini va malumotlarini olish uchun API.\
     Faqat autentifikatsiyadan o‘tgan foydalanuvchi o‘z balansini ko‘ra oladi.",
    responses={
        200: SUserSerializer,
        404: {"description": "Foydalanuvchi topilmadi"},
        401: {"description": "Avtorizatsiya talab qilinadi"},
    },
    tags=["User"]
)
class SUserMeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user = User.objects.get(id=self.request.user.id)
        except User.DoesNotExist:
            return Response({"detail": "User topilmadi."}, status=status.HTTP_404_NOT_FOUND)

        serializer = SUserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    request=SUserChangeEmailSerializer,
    summary="Foydalanuvchining emailini o'zgartirish",
    description="Tizimga kirgan foydalanuvchining emailini o'zgartirish uchun API.\
     Faqat autentifikatsiyadan o‘tgan foydalanuvchi o‘z enailini o'zgartira oladi.",
    responses={
        200: SUserSerializer,
        404: {"description": "Foydalanuvchi topilmadi"},
        401: {"description": "Avtorizatsiya talab qilinadi"},
        400: {"description": "Bunday email mavjud."},
    },
    tags=["User"]
)
class SUserChangeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        serializer = SUserChangeEmailSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Email muvaffaqiyatli o‘zgartirildi"}, status=status.HTTP_200_OK)

class STelegramAccountAPIView(ListCreateAPIView):

    serializer_class = STelegramAccountSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return TelegramAccount.objects.select_related('user').filter(user=self.request.user, is_active=True)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
