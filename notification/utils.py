from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


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
