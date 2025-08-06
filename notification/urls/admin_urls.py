from django.urls import path
from notification.views.admin_views import ANotificationCreateAPIView

urlpatterns = [
    path('notification/create/', ANotificationCreateAPIView.as_view()),
]
