from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from users.views.app_views import SRegisterView, SRegisterGoogleView, SLoginGoogleView, SPasswordChangeView, \
    SPasswordResetEmailView, SPasswordResetConfirmTemplateView, SUserMeAPIView, SUserChangeAPIView, \
    STelegramAccountAPIView

urlpatterns = [
    path('register/', SRegisterView.as_view()),
    path('register/google/', SRegisterGoogleView.as_view()),
    path('login/google/', SLoginGoogleView.as_view()),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('password/change/', SPasswordChangeView.as_view()),
    path('password-reset/', SPasswordResetEmailView.as_view(), name='password-reset'),

    # 2-qadam: Parolni token orqali tiklash
    # path('password-reset-confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(),
    #      name='password-reset-confirm'),
    path('reset-password/<uidb64>/<token>/', SPasswordResetConfirmTemplateView.as_view(),
         name='reset-password-confirm-template'),

    path('user/me/', SUserMeAPIView.as_view(), name='user-me'),
    path('email/change/', SUserChangeAPIView.as_view(), name='email-change'),

    path('telegram-account/', STelegramAccountAPIView.as_view()),
]
