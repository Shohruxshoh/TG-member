from rest_framework import serializers
from django.db import transaction
from order.models import Order
from .models import Country, ServicePrice, Link


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class ServicePriceSerializer(serializers.ModelSerializer):

    class Meta:
        model = ServicePrice
        fields = ['id', 'country', 'category', 'price', 'member', 'percent']
        read_only_fields = ['created_at', 'updated_at']


class LinkSerializer(serializers.ModelSerializer):
    order = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Link
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class OrderWithLinksCreateSerializer(serializers.Serializer):
    service_price = serializers.PrimaryKeyRelatedField(queryset=ServicePrice.objects.all())
    links = serializers.ListField(
        child=serializers.URLField(),  # yoki CharField(), agar URL bo'lmasa
        allow_empty=False
    )

    def create(self, validated_data):
        with transaction.atomic():
            user = self.context['request'].user
            service_price = validated_data['service_price']
            links = validated_data['links']

            # Order yaratish
            order = Order.objects.create(
                user=user,
                service_price=service_price,
                price=service_price.price,
                status='PENDING',
            )

            # Har bir link uchun Link obyekti yaratamiz
            link_objs = [Link(order=order, link=link) for link in links]
            Link.objects.bulk_create(link_objs)

        return {
            "order_id": order.id,
            "links": links
        }