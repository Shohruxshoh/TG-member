from django.shortcuts import render
from rest_framework.generics import CreateAPIView, ListCreateAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from service.schemas import COMMON_RESPONSES
from users.models import User, TelegramAccount
from rest_framework.permissions import AllowAny, IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse
from django.views import View
from django.http import JsonResponse
from users.serializers.app_serializers import SRegisterSerializer, SRegisterGoogleSerializer, SLoginGoogleSerializer, \
    SPasswordChangeSerializer, SPasswordResetEmailRequestSerializer, SPasswordResetConfirmSerializer, SUserSerializer, \
    SUserChangeEmailSerializer, STelegramAccountSerializer


# Create your views here.
@extend_schema(
    request=SRegisterSerializer,
    responses={
        200: OpenApiResponse(
            response=SRegisterSerializer
        ),
        **COMMON_RESPONSES
    }
)
class SRegisterView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = SRegisterSerializer
    permission_classes = [AllowAny]


@extend_schema(
    request=SRegisterGoogleSerializer,
    responses={
        200: OpenApiResponse(
            response=SRegisterGoogleSerializer
        ),
        **COMMON_RESPONSES
    }
)
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
            **COMMON_RESPONSES
        },
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
            200: OpenApiResponse(response=SPasswordChangeSerializer, description="Password changed successfully."),
            **COMMON_RESPONSES
        },
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
        responses={200: {"description": "Recovery link sent"},
                   **COMMON_RESPONSES
                   }
    )
    def post(self, request):
        serializer = SPasswordResetEmailRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(request)
        return Response({"message": "A password reset link has been sent to your email."}, status=status.HTTP_200_OK)


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
    summary="Get user information",
    description="API to retrieve the balance and information of a logged-in user.\
     Only authenticated users can see their balance.",
    responses={
        200: SUserSerializer,
        **COMMON_RESPONSES
    },
    tags=["users"]
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
    summary="Change user email",
    description="API to change the email of a logged in user.\
     Only authenticated users can change their email address..",
    responses={
        200: SUserSerializer,
        **COMMON_RESPONSES
    },
    tags=["users"]
)
class SUserChangeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        serializer = SUserChangeEmailSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Email changed successfully."}, status=status.HTTP_200_OK)


@extend_schema(
    responses={
        200: OpenApiResponse(
            response=STelegramAccountSerializer
        ),
        **COMMON_RESPONSES
    }
)
class STelegramAccountAPIView(ListCreateAPIView):
    serializer_class = STelegramAccountSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return TelegramAccount.objects.select_related('user').filter(user=self.request.user, is_active=True)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
