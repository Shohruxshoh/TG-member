from django.urls import path
from notification.views.app_views import SNotificationListAPIView

urlpatterns = [
    path('', SNotificationListAPIView.as_view()),
]
