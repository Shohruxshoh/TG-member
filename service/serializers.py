from rest_framework import serializers
from django.db import transaction
from order.models import Order
from .models import Country, Service, Link


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ['id', 'name', 'icon', 'is_active']
        read_only_fields = ['created_at', 'updated_at']


class ServiceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Service
        fields = ['id', 'country', 'category', 'price', 'member', 'percent', 'post', 'is_active']
        read_only_fields = ['created_at', 'updated_at']


class LinkSerializer(serializers.ModelSerializer):
    order = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Link
        fields = ['id', 'order', 'link', 'is_active']
        read_only_fields = ['created_at', 'updated_at']


class OrderWithLinksCreateSerializer(serializers.Serializer):
    service = serializers.PrimaryKeyRelatedField(queryset=Service.objects.all())
    links = serializers.ListField(
        child=serializers.CharField(),  # yoki CharField(), agar URL bo'lmasa
        allow_empty=False
    )

    def create(self, validated_data):
        with transaction.atomic():
            user = self.context['request'].user
            service = validated_data['service']
            links = validated_data['links']

            # Order yaratish
            order = Order.objects.create(
                user=user,
                service=service,
                member=service.member,
                service_category= service.category,
                price=service.price,
                status='PENDING',
            )

            # Har bir link uchun Link obyekti yaratamiz
            link_objs = [Link(order=order, link=link) for link in links]
            Link.objects.bulk_create(link_objs)

        return {
            "order_id": order.id,
            "links": links
        }