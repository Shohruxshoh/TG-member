from django.contrib import admin
from .models import Notification
from .utils import send_topic_notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("title", "created_at")

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        # Firebase topic ga yuborish
        response = send_topic_notification("all", obj.title, obj.description)

        self.message_user(request, f"Notification yuborildi ✅ Firebase Response: {response}")