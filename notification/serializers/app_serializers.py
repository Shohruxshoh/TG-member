from rest_framework import serializers
from notification.models import Notification


class SNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'title', 'description', 'image', 'created_at', 'updated_at']
