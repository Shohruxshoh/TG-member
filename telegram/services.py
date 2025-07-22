# from typing import Optional
# from django.utils import timezone
# from django.db import transaction
# from telethon.errors import RPCError
#
# from .telethon_client import get_telegram_client
# from .utils import parse_telegram_url, resolve_entity_and_channel_model
# from .models import TelegramPost, TelegramChannel
#
#
# async def fetch_single_message(client, entity, msg_id: int):
#     """Return Telethon Message or None if not found."""
#     try:
#         msg = await client.get_messages(entity, ids=msg_id)
#         # Telethon get_messages returns message or list; unify
#         if isinstance(msg, list):
#             msg = msg[0] if msg else None
#         return msg or None
#     except RPCError:
#         return None
#
#
# def _message_to_post_kwargs(channel_obj: TelegramChannel, message) -> dict:
#     """Map Telethon message to TelegramPost fields."""
#     return dict(
#         channel=channel_obj,
#         message_id=message.id,
#         date=message.date.astimezone(timezone.utc),
#         text=message.message or "",
#         has_media=bool(message.media),
#         raw_data=message.to_dict(),  # optional; large
#     )
#
#
# @transaction.atomic
# def _save_message(channel_obj: TelegramChannel, message) -> TelegramPost:
#     values = _message_to_post_kwargs(channel_obj, message)
#     obj, created = TelegramPost.objects.update_or_create(
#         channel=channel_obj,
#         message_id=message.id,
#         defaults=values,
#     )
#     return obj
#
#
# async def backfill_previous_posts_from_url(url: str, count: int = 50, *, save_raw: bool = True) -> dict:
#     """Given a Telegram message URL, backfill the previous `count` posts.
#
#     Returns summary dict: {
#         'checked': int,
#         'found': int,
#         'saved': int,
#         'skipped_missing': int,
#         'start_message_id': int,
#         'end_message_id': int,
#     }
#     """
#     username_like, ref_msg_id = parse_telegram_url(url)
#     if ref_msg_id is None:
#         raise ValueError("URL does not include a message id; cannot backfill.")
#
#     client = get_telegram_client()
#     await client.connect()
#     if not await client.is_user_authorized():
#         # NOTE: You must run .start() somewhere interactive to sign in.
#         await client.start()  # will prompt if no saved session; or pre-auth session.
#
#     channel_obj, entity = await resolve_entity_and_channel_model(client, username_like)
#
#     checked = found = saved = skipped_missing = 0
#
#     # We'll examine IDs: ref_msg_id-1 down to ref_msg_id-count (inclusive lower bound > 0)
#     start_id = ref_msg_id - 1
#     end_id = max(ref_msg_id - count, 0)
#
#     current_id = start_id
#     while current_id > end_id:
#         checked += 1
#         msg = await fetch_single_message(client, entity, current_id)
#         if msg is None:
#             skipped_missing += 1
#         else:
#             found += 1
#             obj = _save_message(channel_obj, msg)
#             if obj:
#                 saved += 1  # counts update_or_create as save
#         current_id -= 1
#
#     return {
#         "checked": checked,
#         "found": found,
#         "saved": saved,
#         "skipped_missing": skipped_missing,
#         "start_message_id": start_id,
#         "end_message_id": end_id,
#     }
