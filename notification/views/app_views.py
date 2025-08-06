from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from notification.models import Notification
from notification.serializers.app_serializers import SNotificationSerializer


class SNotificationListAPIView(generics.ListAPIView):
    queryset = Notification.objects.filter(is_active=True).order_by('-created_at')
    serializer_class = SNotificationSerializer
    permission_classes = [IsAuthenticated]
