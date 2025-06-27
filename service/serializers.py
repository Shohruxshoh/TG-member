from rest_framework import serializers

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


class LinkCreateSerializer(serializers.ModelSerializer):
    service_price = serializers.PrimaryKeyRelatedField(queryset=ServicePrice.objects.all(), write_only=True)

    class Meta:
        model = Link
        fields = ['link', 'service_price']  # order emas, faqat keraklilar
        extra_kwargs = {
            'link': {'required': True}
        }

    def create(self, validated_data):
        request = self.context['request']
        user = request.user
        service_price = validated_data.pop('service_price')
        print(service_price)

        # Order yaratish
        order = Order.objects.create(
            service_price=service_price,
            user=user,
            price=service_price.price,
            status='PENDING',
        )

        # Link yaratish
        link = Link.objects.create(order=order, **validated_data)
        return link
