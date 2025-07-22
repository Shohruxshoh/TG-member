from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from users.view import RegisterView, RegisterGoogleView, LoginGoogleView, PasswordChangeView, PasswordResetEmailView, \
    PasswordResetConfirmTemplateView, UserMeAPIView, UserChangeAPIView, TelegramAccountAPIView

urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('register/google/', RegisterGoogleView.as_view()),
    path('login/google/', LoginGoogleView.as_view()),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('password/change/', PasswordChangeView.as_view()),
    path('password-reset/', PasswordResetEmailView.as_view(), name='password-reset'),

    # 2-qadam: Parolni token orqali tiklash
    # path('password-reset-confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(),
    #      name='password-reset-confirm'),
    path('reset-password/<uidb64>/<token>/', PasswordResetConfirmTemplateView.as_view(),
         name='reset-password-confirm-template'),

    path('user/me/', UserMeAPIView.as_view(), name='user-me'),
    path('email/change/', UserChangeAPIView.as_view(), name='email-change'),

    path('telegram-account/', TelegramAccountAPIView.as_view()),
]
