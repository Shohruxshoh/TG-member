import os
from django.conf import settings
from telethon import TelegramClient

# Single, reusable Telethon client instance (lazy-init pattern)
_client = None


def get_telegram_client():
    global _client
    if _client is None:
        api_id = settings.TELEGRAM_API_ID
        api_hash = settings.TELEGRAM_API_HASH
        session_name = getattr(settings, "TELEGRAM_SESSION_NAME", "tg_session")
        _client = TelegramClient(session_name, api_id, api_hash)
    return _client
