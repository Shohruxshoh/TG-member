# import re
# from urllib.parse import urlparse
# from typing import Tuple
# from telethon.tl.types import InputPeerChannel, Channel, Chat, PeerChannel
# from telethon.errors import UsernameInvalidError, UsernameNotOccupiedError
#
# TELEGRAM_URL_RE = re.compile(r"https?://t\.me/(c/)?([^/]+)/?(\d+)?/?$", re.IGNORECASE)
#
#
# def parse_telegram_url(url: str) -> Tuple[str | None, int | None]:
#     """Return (username_or_c_prefix, message_id) from t.me style URL.
#
#     Supports:
#       https://t.me/username/12345  -> ("username", 12345)
#       https://t.me/c/123456789/55  -> ("c/123456789", 55)  # private link numeric form
#
#     If message id missing, returns None.
#     """
#     m = TELEGRAM_URL_RE.match(url.strip())
#     if not m:
#         raise ValueError(f"URL not recognized as Telegram link: {url}")
#     c_prefix, name_or_id, msg_id = m.groups()
#     username_like = ("c/" + name_or_id) if c_prefix else name_or_id
#     return username_like, int(msg_id) if msg_id else None
#
#
# async def resolve_entity_and_channel_model(client, username_like: str) -> TelegramChannel:
#     """Resolve Telethon entity from username_or_cid, and ensure TelegramChannel row.
#
#     username_like examples:
#       - "somechannel"
#       - "c/123456789" (private numeric)
#     """
#     from .models import TelegramChannel  # local import to avoid circular
#
#     # Detect private numeric link form: c/<internal_id>
#     if username_like.startswith("c/"):
#         # Telethon can't directly resolve t.me/c internal ids; need invite link or joined entity.
#         # If you already track tg_id in DB, try lookup. Else raise.
#         # For this template, we assume you *already* have the channel row if using c/ links.
#         internal_id = int(username_like.split("/", 1)[1])
#         channel_obj = TelegramChannel.objects.filter(tg_id=internal_id).first()
#         if not channel_obj:
#             raise ValueError("Private t.me/c link can't be resolved automatically. Please supply channel tg_id.")
#         entity = await client.get_entity(PeerChannel(channel_obj.tg_id))
#         return channel_obj, entity
#
#     # Public username
#     try:
#         entity = await client.get_entity(username_like)
#     except (UsernameInvalidError, UsernameNotOccupiedError) as e:
#         raise ValueError(f"Channel username not found: {username_like}") from e
#
#     # Ensure DB row
#     if isinstance(entity, Channel):
#         channel_obj, _ = TelegramChannel.objects.get_or_create(
#             username=username_like,
#             defaults={
#                 "tg_id": entity.id,
#                 "access_hash": entity.access_hash,
#                 "title": entity.title or "",
#                 "is_megagroup": bool(entity.megagroup),
#                 "is_broadcast": bool(entity.broadcast),
#             },
#         )
#         # Update if changed
#         changed = False
#         if channel_obj.tg_id != entity.id:
#             channel_obj.tg_id = entity.id; changed = True
#         if channel_obj.access_hash != entity.access_hash:
#             channel_obj.access_hash = entity.access_hash; changed = True
#         if channel_obj.title != (entity.title or ""):
#             channel_obj.title = entity.title or ""; changed = True
#         if changed:
#             channel_obj.save(update_fields=["tg_id", "access_hash", "title"])
#         return channel_obj, entity
#
#     # Groups may resolve as Chat
#     if isinstance(entity, Chat):
#         channel_obj, _ = TelegramChannel.objects.get_or_create(
#             username=username_like,
#             defaults={
#                 "tg_id": entity.id,
#                 "title": entity.title or "",
#                 "is_megagroup": False,
#                 "is_broadcast": False,
#             },
#         )
#         return channel_obj, entity
#
#     raise TypeError(f"Unsupported entity type returned for {username_like}: {type(entity)!r}")