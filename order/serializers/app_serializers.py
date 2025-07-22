import re

from rest_framework import serializers
from django.db import transaction
from service.models import Link, Service
from order.models import Order


class SOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'service', 'status', 'price', 'member', 'service_category', 'created_at']
        read_only_fields = ['price', 'member', 'service_category', 'created_at']


class SChildOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'status', 'price', 'member', 'service_category', 'created_at']


class SOrderDetailSerializer(serializers.ModelSerializer):
    children = SChildOrderSerializer(many=True, read_only=True)
    # self_members = serializers.IntegerField(read_only=True, source='total_members_anno')
    calculated_total = serializers.DecimalField(
        max_digits=20, decimal_places=2, read_only=True
    )

    class Meta:
        model = Order
        fields = [
            'id', 'user', 'status', 'price', 'member', 'service_category', 'self_members', 'calculated_total',
            'is_active', 'created_at', 'updated_at', 'children'
        ]


class SOrderWithLinksChildCreateSerializer(serializers.Serializer):
    service = serializers.PrimaryKeyRelatedField(queryset=Service.objects.all())
    links = serializers.ListField(
        child=serializers.CharField(),  # yoki CharField(), agar URL bo'lmasa
        allow_empty=False
    )
    # kanal_name = serializers.CharField(max_length=200)

    def create(self, validated_data):
        with transaction.atomic():
            user = self.context['request'].user
            service = validated_data['service']
            links = validated_data['links']
            # kanal_name = validated_data['kanal_name']
            # Order yaratish
            order = Order.objects.create(
                user=user,
                service=service,
                member=service.member,
                service_category=service.category,
                price=service.price,
                status='PENDING',
            )

            child_order = [Order(
                parent=order,
                user=user,
                service=service,
                member=service.member,
                service_category=service.category,
                price=service.price / len(links),
                status='PENDING',
            ) for _ in links]
            Order.objects.bulk_create(child_order)
            # Har bir link uchun Link obyekti yaratamiz
            link_objs = [Link(order=order, link=link) for link in links]
            Link.objects.bulk_create(link_objs)

        return {
            "order_id": order.pk,
            "links": links
        }


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
            # Order yaratish
            order = Order.objects.create(
                user=user,
                service=service,
                member=service.member,
                service_category=service.category,
                price=service.price,
                status='PENDING',
            )
            Link.objects.create(order=order, link=link, channel_name=channel_name)

        return {
            "order_id": order.pk,
            "links": link,
            "channel_name":channel_name
        }


_TELEGRAM_URL_VALID_RE = re.compile(r"https?://t\.me/(c/)?[^/]+/\d+/?$", re.IGNORECASE)


class STelegramBackfillSerializer(serializers.Serializer):
    service_id = serializers.IntegerField()
    url = serializers.URLField()
    count = serializers.IntegerField(min_value=1, max_value=500, required=False, default=50)

    def validate_url(self, value: str):
        if not _TELEGRAM_URL_VALID_RE.match(value.strip()):
            raise serializers.ValidationError("Telegram post URL noto'g'ri formatda.")
        return value

    def validate_service_id(self, value: int):
        if not Service.objects.filter(pk=value).exists():
            raise serializers.ValidationError("Bunday xizmat mavjud emas.")
        return value

    def create(self, validated_data):
        # Serializer .save() chaqirilsa, hech narsa yaratmaymiz; view/service ishlatadi.
        return validated_data

    def update(self, instance, validated_data):
        raise NotImplementedError("Yangilash qo'llab-quvvatlanmaydi.")
