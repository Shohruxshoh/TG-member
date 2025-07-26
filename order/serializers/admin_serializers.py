from rest_framework import serializers
from order.models import Order


class OrderSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = ['user', 'price', 'member', 'service_category', 'created_at', 'updated_at']


class OrderDetailSerializer(serializers.ModelSerializer):
    service = serializers.StringRelatedField()

    class Meta:
        model = Order
        fields = ['id', 'service', 'status', 'price', 'member', 'service_category', 'created_at']
