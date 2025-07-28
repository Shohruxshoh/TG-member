import re
from django.db.models import F
from rest_framework import serializers
from django.db import transaction
from rest_framework.exceptions import ValidationError
from balance.models import Balance, Vip
from service.models import Service
from order.models import Order, OrderMember
from users.models import TelegramAccount
from datetime import timedelta
from django.utils import timezone


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
            'id', 'user', 'status', 'price', 'member', 'service_category', 'link', 'channel_name', 'self_members',
            'calculated_total', 'is_active', 'created_at', 'updated_at', 'children'
        ]


class SOrderLinkListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'link', 'channel_name']


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

    def create(self, validated_data):
        with transaction.atomic():
            user = self.context['request'].user
            service = validated_data['service']
            link = validated_data['link']
            channel_name = validated_data['channel_name']

            # Foydalanuvchi balansi
            try:
                balance = user.user_balance
            except Balance.DoesNotExist:
                raise ValidationError("User balance not found.")

            # Balans yetarli ekanligini tekshirish
            if balance.balance < service.price:
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
                status='PENDING',
            )

            # Link yaratish
            # Link.objects.create(order=order, link=link, channel_name=channel_name)

            # Balansdan narxni ayirish
            balance.balance = F('balance') - service.price
            balance.save()
            balance.refresh_from_db()

            return {
                "order_id": order.pk,
                "links": link,
                "channel_name": channel_name
            }


_TELEGRAM_URL_VALID_RE = re.compile(r"https?://t\.me/(c/)?[^/]+/\d+/?$", re.IGNORECASE)


class STelegramBackfillSerializer(serializers.Serializer):
    service_id = serializers.IntegerField()
    url = serializers.URLField()
    count = serializers.IntegerField(min_value=1, max_value=500, required=False, default=50)

    def validate_url(self, value: str):
        if not _TELEGRAM_URL_VALID_RE.match(value.strip()):
            raise serializers.ValidationError("Telegram post URL is in the wrong format.")
        return value

    def validate_service_id(self, value: int):
        if not Service.objects.filter(pk=value).exists():
            raise serializers.ValidationError("Such a service does not exist.")
        return value

    def create(self, validated_data):
        # Serializer .save() chaqirilsa, hech narsa yaratmaymiz; view/service ishlatadi.
        return validated_data

    def update(self, instance, validated_data):
        raise NotImplementedError("Update is not supported.")


class SAddVipSerializer(serializers.Serializer):
    telegram_id = serializers.IntegerField()
    order_id = serializers.IntegerField()

    def validate(self, attrs):
        telegram_id = attrs.get("telegram_id")
        order_id = attrs.get("order_id")

        # TelegramAccount va Order obyektlarini olish
        try:
            telegram = TelegramAccount.objects.get(telegram_id=telegram_id, is_active=True)
        except TelegramAccount.DoesNotExist:
            raise serializers.ValidationError({"telegram_id": "Such a telegram does not exist or is inactive."})

        try:
            order = Order.objects.get(pk=order_id, is_active=True)
        except Order.DoesNotExist:
            raise serializers.ValidationError({"order_id": "Such an order does not exist or is inactive."})

        # 3 kun ichida shu telegram orderda bormi?
        three_days_ago = timezone.now() - timedelta(days=3)
        recent_member_exists = OrderMember.objects.filter(
            order=order,
            telegram=telegram,
            joined_at__gte=three_days_ago
        ).exists()

        if recent_member_exists:
            raise serializers.ValidationError(
                "This Telegram account has already joined this order within the last 3 days.")

        attrs['telegram'] = telegram
        attrs['order'] = order
        return attrs

    def create(self, validated_data):
        with transaction.atomic():
            user = self.context['request'].user
            telegram = validated_data['telegram']
            order = validated_data['order']
            vip = Vip.objects.filter(category=order.service_category, is_active=True).first()
            if not vip:
                raise serializers.ValidationError("No VIP configuration found for this category.")
            OrderMember.objects.create(
                telegram_id=telegram.id,
                order_id=order.id,
                user=user
            )
            user.user_balance.balance = F('balance') + vip.vip
            user.user_balance.save()
            user.user_balance.refresh_from_db()
        return validated_data
