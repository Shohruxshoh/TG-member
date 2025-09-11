from celery import shared_task
from .models import OrderMember
from users.models import User
from django.db.models import Sum, F
from django.utils.timezone import now
from datetime import timedelta
from asgiref.sync import async_to_sync
from service.models import Service
from .telegram_fetch import fetch_prior_message_urls
from .services import save_links_for_order


@shared_task
def process_telegram_checklist(data, user_id):
    """
    Telegram id + order id larni tekshiradi va kerakli o'zgarishlarni DB da qiladi.
    """
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return {"error": "User not found"}

    cutoff_time = now() - timedelta(minutes=1)

    # 1️⃣ Telegram va order ID larni yig‘ish
    all_telegram_ids = [item["telegram_id"] for item in data]
    all_order_ids = [ch["order_id"] for item in data for ch in item["channels"]]

    # 2️⃣ Faqat kerakli a’zolarni olish
    qs = OrderMember.objects.filter(
        telegram__telegram_id__in=all_telegram_ids,
        order_id__in=all_order_ids,
        is_active=True,
        joined_at__lt=cutoff_time
    )

    # 3️⃣ VIP yig‘ish — bitta query orqali
    user_vip = qs.aggregate(total_vip=Sum("vip"))["total_vip"] or 0

    # 4️⃣ bulk_update o‘rniga bitta update()
    updated_count = qs.update(is_active=False)

    # 5️⃣ Balansni yangilash
    if user_vip and hasattr(user, "user_balance"):
        user.user_balance.balance = F("balance") + user_vip
        user.user_balance.save(update_fields=["balance"])

    return {"balance_added": user_vip}


@shared_task
def delete_expired_subscriptions():
    cutoff_time = now() - timedelta(minutes=1)
    qs = OrderMember.objects.filter(is_active=True, joined_at__lt=cutoff_time)
    count = qs.count()
    qs.update(is_active=False)
    return {"deleted": count}




@shared_task(bind=True)
def backfill_telegram_links(self, service_id, user_id, url, count, channel_name, channel_id):
    """
    Telegramdan xabarlarni olib kelib DBga saqlash.
    Progressni kuzatish uchun self.update_state() ishlatamiz.
    """

    try:
        service = Service.objects.get(pk=service_id)
    except Service.DoesNotExist:
        return {"error": "Service not found."}

    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return {"error": "User not found."}

    try:
        self.update_state(state="FETCHING")
        urls = async_to_sync(fetch_prior_message_urls)(url, count)
    except Exception as e:
        return {"error": f"Telegram fetch error: {e}"}

    self.update_state(state="SAVING")
    save_result = save_links_for_order(service, user, urls, channel_name, channel_id)

    return {
        "requested": count,
        "fetched_from_telegram": len(urls),
        "saved_to_db": save_result["created"],
        "already_in_db": save_result["existing"],
    }