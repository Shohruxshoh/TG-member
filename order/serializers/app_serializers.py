import re
from django.db.models import F
from django.utils.timezone import now
from rest_framework import serializers
from django.db import transaction
from rest_framework.exceptions import ValidationError
from balance.models import Balance, Vip
from order.enums import Status
from service.models import Service
from order.models import Order, OrderMember
from users.models import TelegramAccount
from django.shortcuts import get_object_or_404
from datetime import timedelta
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


class SOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'service', 'status', 'price', 'member', 'link', 'channel_name', 'service_category',
                  'created_at']
        read_only_fields = ['price', 'member', 'service_category', 'created_at']


class SChildOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'status', 'price', 'member', 'service_category', 'link', 'channel_name', 'created_at']


class SOrderDetailSerializer(serializers.ModelSerializer):
    children = SChildOrderSerializer(many=True, read_only=True)
    # self_members = serializers.IntegerField(read_only=True, source='total_members_anno')
    calculated_total = serializers.DecimalField(
        max_digits=20, decimal_places=2, read_only=True
    )

    class Meta:
        model = Order
        fields = [
            'id', 'user', 'status', 'price', 'member', 'service_category', 'link', 'channel_name', 'channel_id', 'day',
            'self_members', 'calculated_total', 'is_active', 'created_at', 'updated_at', 'children'
        ]


class SOrderLinkListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'link', 'channel_name', 'channel_id']  # , 'country_code'


# class SOrderWithLinksChildCreateSerializer(serializers.Serializer):
#     service = serializers.PrimaryKeyRelatedField(queryset=Service.objects.all())
#     links = serializers.ListField(
#         child=serializers.CharField(),  # yoki CharField(), agar URL bo'lmasa
#         allow_empty=False
#     )
#     # kanal_name = serializers.CharField(max_length=200)
#
#     def create(self, validated_data):
#         with transaction.atomic():
#             user = self.context['request'].user
#             service = validated_data['service']
#             links = validated_data['links']
#             # kanal_name = validated_data['kanal_name']
#             # Order yaratish
#             order = Order.objects.create(
#                 user=user,
#                 service=service,
#                 member=service.member,
#                 service_category=service.category,
#                 price=service.price,
#                 status='PENDING',
#             )
#
#             child_order = [Order(
#                 parent=order,
#                 user=user,
#                 service=service,
#                 member=service.member,
#                 service_category=service.category,
#                 price=service.price / len(links),
#                 status='PENDING',
#             ) for _ in links]
#             Order.objects.bulk_create(child_order)
#             # Har bir link uchun Link obyekti yaratamiz
#             link_objs = [Link(order=order, link=link) for link in links]
#             Link.objects.bulk_create(link_objs)
#
#         return {
#             "order_id": order.pk,
#             "links": links
#         }


class SOrderLinkCreateSerializer(serializers.Serializer):
    service = serializers.PrimaryKeyRelatedField(queryset=Service.objects.all())
    link = serializers.CharField(max_length=250, required=True)
    channel_name = serializers.CharField(max_length=200)
    channel_id = serializers.IntegerField()

    def create(self, validated_data):
        with transaction.atomic():
            user = self.context['request'].user
            service = validated_data['service']
            link = validated_data['link']
            channel_name = validated_data['channel_name']
            channel_id = validated_data['channel_id']

            logger.info(f"User {user.id} is creating an order for service {service.id}")

            # Foydalanuvchi balansi
            try:
                balance = user.user_balance
            except Balance.DoesNotExist:
                logger.error(f"Balance not found for user {user.id}")
                raise ValidationError("User balance not found.")

            # Balans yetarli ekanligini tekshirish
            if balance.balance < service.price:
                logger.warning(f"User {user.id} has insufficient balance: {balance.balance}, required: {service.price}")
                raise ValidationError("Your balance is insufficient.")

            # Order yaratish
            order = Order.objects.create(
                user=user,
                service=service,
                member=service.member,
                service_category=service.category,
                price=service.price,
                link=link,
                channel_name=channel_name,
                channel_id=channel_id,
                country_code=service.country.country_code,
                day=service.day.day,
                status=Status.PENDING,
            )

            logger.info(f"Order {order.id} created by user {user.id}")

            # Balansdan narxni ayirish
            balance.balance = F('balance') - service.price
            balance.save()
            balance.refresh_from_db()

            logger.info(
                f"User {user.id} balance updated after creating order {order.id}. New balance: {balance.balance}")

            return {
                "order_id": order.pk,
                "links": link,
                "channel_name": channel_name
            }


_TELEGRAM_URL_VALID_RE = re.compile(r"^https?://t\.me/(c/)?[^/]+/\d+/?$", re.IGNORECASE)


class STelegramBackfillSerializer(serializers.Serializer):
    service_id = serializers.IntegerField()
    url = serializers.URLField()
    count = serializers.IntegerField(min_value=1, max_value=500, required=False, default=50)
    channel_id = serializers.CharField(max_length=200, required=False, allow_blank=True)
    channel_name = serializers.CharField(max_length=200, required=False, allow_blank=True)

    def validate_url(self, value: str):
        value = value.strip()
        if not _TELEGRAM_URL_VALID_RE.fullmatch(value):
            raise serializers.ValidationError("Telegram post URL is in the wrong format.")
        return value

    def validate_service_id(self, value: int):
        # Viewda get_object_or_404 ishlatilgani uchun bu yerda faqat mavjudligini tekshirish kifoya
        if not Service.objects.filter(pk=value).exists():
            raise serializers.ValidationError("Such a service does not exist.")
        return value

    def validate(self, attrs):
        """
        service_id orqali servisni olib, foydalanuvchining balansini tekshiramiz.
        Bu validate() ichida bo'lishi kerak, create emas, chunki bu faqat validatsiya uchun ishlatilmoqda.
        """
        service_id = attrs['service_id']
        service = get_object_or_404(Service, pk=service_id)
        user = self.context['request'].user

        balance = getattr(user, 'user_balance', None)
        if not balance:
            raise serializers.ValidationError("Balance is not available.")

        if balance.balance < service.price:
            raise serializers.ValidationError("There are not enough funds on the balance.")

        return attrs

    def create(self, validated_data):
        # Bu serializer hech qanday obyekt yaratmaydi, faqat validatsiya uchun.
        return validated_data

    def update(self, instance, validated_data):
        raise NotImplementedError("Update is not supported.")


class SAddVipSerializer(serializers.Serializer):
    telegram_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        allow_empty=False
    )
    order_id = serializers.IntegerField(min_value=1)

    def validate(self, attrs):
        telegram_ids = attrs['telegram_ids']
        order_id = attrs['order_id']

        try:
            order = Order.objects.get(pk=order_id, is_active=True)
        except Order.DoesNotExist:
            raise serializers.ValidationError({"order_id": "Order not found or inactive."})

        three_days_ago = timezone.now() - timedelta(days=3)

        # Barcha TelegramAccount'larni bitta so‘rov bilan olib kelamiz
        telegrams = TelegramAccount.objects.filter(
            telegram_id__in=telegram_ids,
            is_active=True,
            country_code=order.country_code
        )

        # Faqat orderga oxirgi 3 kunda qo‘shilmaganlar
        existing_recent_members = set(OrderMember.objects.filter(
            order=order,
            telegram__telegram_id__in=telegram_ids,
            joined_at__gte=three_days_ago
        ).values_list("telegram__telegram_id", flat=True))

        # Toza ro‘yxat
        valid_telegrams = [
            tg for tg in telegrams
            if tg.telegram_id not in existing_recent_members
        ]

        if not valid_telegrams:
            raise serializers.ValidationError({"telegram_ids": "No valid Telegram accounts to add."})

        attrs['order'] = order
        attrs['valid_telegrams'] = valid_telegrams
        return attrs

    def create(self, validated_data):
        user = self.context['request'].user
        order = validated_data['order']
        telegrams = validated_data['valid_telegrams']

        with transaction.atomic():
            # Order lock
            order = Order.objects.select_for_update().get(id=order.id)

            current_count = OrderMember.objects.filter(order=order, is_active=True).count()
            remaining_slots = order.member - current_count
            if remaining_slots <= 0:
                raise serializers.ValidationError("Order is already full.")

            selected_telegrams = telegrams[:remaining_slots]

            vip = Vip.objects.filter(category=order.service_category, is_active=True).first()
            if not vip:
                raise serializers.ValidationError("VIP config not found for this category.")

            now = timezone.now()
            members_to_create = [
                OrderMember(
                    telegram=tg,
                    user=user,
                    order=order,
                    member_duration=order.day,
                    vip=vip.vip,
                    is_active=True,
                    joined_at=now
                )
                for tg in selected_telegrams
            ]
            created_members = OrderMember.objects.bulk_create(members_to_create, batch_size=50)

            # # Balans yangilash (F expression orqali — parallelizmga chidamli)
            # from django.db.models import F
            # user.user_balance.__class__.objects.filter(user=user).update(
            #     balance=F('balance') + vip.vip * len(created_members)
            # )

            # Agar to‘ldi, statusni yangilash
            if order.member == order.self_members:
                order.status = Status.COMPLETED
                order.number_added = order.self_members
                order.save(update_fields=['status'])

        return created_members


class SCheckAddedChannelSerializer(serializers.Serializer):
    telegram_id = serializers.IntegerField()
    order_id = serializers.IntegerField()

    def validate(self, attrs):
        telegram_id = attrs.get("telegram_id")
        order_id = attrs.get("order_id")

        try:
            telegram = TelegramAccount.objects.select_related('user').get(telegram_id=telegram_id, is_active=True)
        except TelegramAccount.DoesNotExist:
            raise serializers.ValidationError({"telegram_id": "Such a telegram does not exist or is inactive."})

        try:
            order = Order.objects.get(pk=order_id, is_active=True)
        except Order.DoesNotExist:
            raise serializers.ValidationError({"order_id": "Such an order does not exist or is inactive."})

        three_days_ago = timezone.now() - timedelta(days=3)
        recent_member_exists = OrderMember.objects.select_related('order', 'telegram', 'user').filter(
            order=order,
            telegram=telegram,
            joined_at__gte=three_days_ago
        ).exists()

        # Save the result in serializer for later use
        attrs['is_recent_member'] = recent_member_exists
        return attrs


class ChannelSerializer(serializers.Serializer):
    order_id = serializers.IntegerField(min_value=1)
    channel_id = serializers.CharField(max_length=255)


class TelegramDataSerializer(serializers.Serializer):
    telegram_id = serializers.CharField(max_length=50)
    channels = serializers.ListField(
        child=ChannelSerializer(),
        allow_empty=False
    )


class TelegramListSerializer(serializers.ListSerializer):
    child = TelegramDataSerializer()

    def validate(self, data):
        user = self.context['request'].user
        cutoff_time = now() - timedelta(days=2, hours=12)

        # 1️⃣ Telegram va order ID larni yig‘ish
        telegram_orders_map = {}
        all_telegram_ids = set()
        all_order_ids = set()

        for item in data:
            tid = item["telegram_id"]
            orders = [ch["order_id"] for ch in item["channels"]]
            telegram_orders_map[tid] = orders
            all_telegram_ids.add(tid)
            all_order_ids.update(orders)

        # 2️⃣ Faqat keraklilarni DB dan olish (is_active va cutoff_time bo‘yicha filter)
        members = list(
            OrderMember.objects.filter(
                telegram__telegram_id__in=all_telegram_ids,
                order_id__in=all_order_ids,
                is_active=True,
                joined_at__lt=cutoff_time
            ).select_related('telegram')
        )

        # 3️⃣ Mapping yaratish
        members_map = {(m.telegram.telegram_id, m.order_id): m for m in members}

        # 4️⃣ Tekshirish va yangilanishga tayyorlash
        to_update = []
        missing = []
        user_vip = 0

        for tid, order_ids in telegram_orders_map.items():
            for oid in order_ids:
                key = (tid, oid)
                if key in members_map:
                    member = members_map[key]
                    member.is_active = False
                    user_vip += member.vip
                    to_update.append(member)
                # else:
                #     member = members_map[key]
                #     member.is_active = False
                #     user_vip += member.vip
                #     to_update.append(member)

        # if missing:
        #     raise serializers.ValidationError({
        #         "missing": f"Quyidagilar topilmadi: {', '.join(missing)}"
        #     })

        # 5️⃣ bulk_update va balansni yangilash
        if to_update:
            OrderMember.objects.bulk_update(to_update, ["is_active"])
            if hasattr(user, 'user_balance'):
                user.user_balance.balance += user_vip
                user.user_balance.save()

        return data
