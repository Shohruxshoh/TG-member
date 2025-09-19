from rest_framework import serializers
from notification.models import Notification
from notification.utils import send_notification_to_all, send_topic_notification


class ANotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['title', 'description', 'image']

    def save(self, **kwargs):
        instance = Notification.objects.create(**self.validated_data)
        send_topic_notification('news', self.validated_data['title'], self.validated_data['description'],
                                data={"id": f'{instance.pk}'})
        send_notification_to_all(instance)
        return instance
