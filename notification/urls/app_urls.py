from django.urls import path
from notification.views.app_views import SNotificationListAPIView

urlpatterns = [
    path('notifications/', SNotificationListAPIView.as_view()),
]
