from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from firebase_admin import messaging


def send_notification_to_all(notification):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "global_notifications",  # hamma ulangan userlar shu groupda
        {
            "type": "send_notification",
            "title": notification.title,
            "description": notification.description,
            "created_at": str(notification.created_at),
        }
    )


def send_topic_notification(topic: str, title: str, body: str, data: dict = None):
    """
    Firebase topic orqali barcha foydalanuvchilarga yuborish
    """
    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body,
        ),
        topic=topic,
        data=data or {},
    )
    response = messaging.send(message)
    return response
