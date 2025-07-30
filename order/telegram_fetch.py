import re
from django.conf import settings
from telethon import TelegramClient

TELEGRAM_URL_RE = re.compile(r"^https?://t\.me/(c/)?([^/]+)/(\d+)/?$", re.IGNORECASE)


def parse_telegram_url(url: str):
    m = TELEGRAM_URL_RE.match(url.strip())
    if not m:
        raise ValueError("Telegram URL noto'g'ri.")
    c_prefix, name_or_id, msg_id = m.groups()
    username_like = ("c/" + name_or_id) if c_prefix else name_or_id
    return username_like, int(msg_id)


async def fetch_prior_message_urls(url: str, count: int):
    """
    Berilgan Telegram post URL dan oldingi `count` ta mavjud xabarni (reverse chronology)
    topadi va har biri uchun to‘liq t.me URL qaytaradi.

    iter_messages => faqat mavjud xabarlar keladi (o‘chirilganlari e'tiborga olinmaydi).
    """
    username_like, ref_msg_id = parse_telegram_url(url)

    # Har chaqiriqda YANGI client — event loop konflikti bo‘lmasin.
    client = TelegramClient(
        getattr(settings, "TELEGRAM_SESSION_NAME", "tg_session"),
        settings.TELEGRAM_API_ID,
        settings.TELEGRAM_API_HASH,
    )

    async with client:
        # Session oldindan autentifikatsiya qilingan bo‘lishi kerak (CLI orqali bir marta login qilib qo‘ying).
        if not await client.is_user_authorized():
            # Web API kontekstida kod kiritishning iloji yo‘q -> oldindan login shart.
            raise RuntimeError("Telethon session autorize qilinmagan. Avval CLI orqali login qiling.")

        entity = await client.get_entity(username_like)
        count -= 1 if count > 1 else 0

        # t.me/c/... yoki t.me/<username>/... shaklini to‘g‘ri yasash
        if username_like.startswith("c/"):
            base_part = username_like  # allaqachon 'c/<internal>'
        else:
            base_part = username_like  # kanal username

        urls = [f"https://t.me/{base_part}/{ref_msg_id}"]

        async for msg in client.iter_messages(entity, offset_id=ref_msg_id, limit=count):
            print(50, f"https://t.me/{base_part}/{msg.id}")
            urls.append(f"https://t.me/{base_part}/{msg.id}")

    return urls
