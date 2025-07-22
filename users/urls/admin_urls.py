from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from users.views.admin_views import AUserListAPIView, AUserChangeAPIView, AUserMeAPIView, \
    APasswordResetConfirmTemplateView, APasswordResetEmailView, APasswordChangeView, ALoginGoogleView, \
    ATelegramAccountAPIView

urlpatterns = [
    path('login/google/', ALoginGoogleView.as_view()),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('password/change/', APasswordChangeView.as_view()),
    path('password-reset/', APasswordResetEmailView.as_view(), name='password-reset'),

    # 2-qadam: Parolni token orqali tiklash
    # path('password-reset-confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(),
    #      name='password-reset-confirm'),
    path('reset-password/<uidb64>/<token>/', APasswordResetConfirmTemplateView.as_view(),
         name='reset-password-confirm-template'),

    path('user/me/', AUserMeAPIView.as_view(), name='user-me'),
    path('email/change/', AUserChangeAPIView.as_view(), name='email-change'),
    path('list/users/', AUserListAPIView.as_view(), name='user-list'),
    path('list/telegram/', ATelegramAccountAPIView.as_view(), name='telegram-list'),
]
