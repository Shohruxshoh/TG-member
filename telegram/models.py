from django.db import models

# Create your models here.
# class TelegramChannel(models.Model):
#     """Represents a Telegram channel/group we're tracking."""
#     # Could be username ("somechannel"), numeric ID, or access hash (if needed).
#     username = models.CharField(max_length=255, unique=True, null=True, blank=True)
#     # Optionally store channel_id + access_hash once resolved via Telethon.
#     tg_id = models.BigIntegerField(null=True, blank=True, db_index=True)
#     access_hash = models.BigIntegerField(null=True, blank=True)
#     title = models.CharField(max_length=512, blank=True)
#     is_megagroup = models.BooleanField(default=False)
#     is_broadcast = models.BooleanField(default=False)
#
#     def __str__(self):
#         return self.username or f"Channel {self.tg_id}"
