from rest_framework import serializers
from notification.models import Notification
from notification.utils import send_notification_to_all


class ANotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['title', 'description', 'image']

    def save(self, **kwargs):
        instance = Notification.objects.create(**self.validated_data)
        send_notification_to_all(instance)
        return instance
