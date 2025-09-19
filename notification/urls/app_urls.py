from django.urls import path
from notification.views.app_views import SNotificationListAPIView, SNotificationDetailAPIView

urlpatterns = [
    path('', SNotificationListAPIView.as_view()),
    path('<int:pk>/', SNotificationDetailAPIView.as_view()),
]
