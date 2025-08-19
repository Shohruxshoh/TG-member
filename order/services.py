# services.py
from django.db import transaction

from order.enums import Status
from service.models import Link, Service
from order.models import Order
from decimal import Decimal


def save_links_for_order(service: Service, user, urls: list[str], channel_name, channel_id) -> dict:
    """
    Parent order yaratadi, har bir noyob URL uchun child order qo'shadi,
    lekin barcha Link-lar parent orderga ulanadi.

    Returns:
        {
            "existing": <int>,  # kirishda chiqqan dublikatlar soni
            "created": <int>,   # yangi URL soni
        }
    """
    if not urls:
        return {"existing": 0, "created": 0}

    # 1) URL-larni tozalash va dublikatlarni chiqarib tashlash
    cleaned = []
    seen = set()
    for raw in urls:
        if raw:
            u = raw.strip()
            if u and u not in seen:
                seen.add(u)
                cleaned.append(u)


    if not cleaned:
        return {"existing": len(urls), "created": 0}

    with transaction.atomic():
        # 2) Parent orderni yaratish
        parent_order = Order.objects.create(
            user=user,
            service=service,
            member=service.member,
            service_category=service.category,
            day=service.day.day,
            price=service.price,
            link=cleaned[0],
            channel_name=channel_name,
            channel_id=channel_id,
            country_code=service.country.country_code,
            status=Status.PENDING,
        )

        count = len(cleaned)
        unit_price = Decimal(service.price) / count if count else Decimal("0")

        # 3) Child orderlar tayyorlash
        child_orders = [
            Order(
                parent=parent_order,
                user=user,
                service=service,
                member=service.member,
                service_category=service.category,
                price=unit_price,
                day=service.day.day,
                link=url,
                channel_name=channel_name,
                channel_id=channel_id,
                status=Status.PENDING,
            )
            for url in cleaned
        ]
        Order.objects.bulk_create(child_orders)

        # 4) Linklar faqat parent orderga bog‘lanadi
        # links = [Link(order=parent_order, link=url) for url in cleaned]
        # Link.objects.bulk_create(links)

    return {
        "existing": len(urls) - len(cleaned),
        "created": len(cleaned),
    }
