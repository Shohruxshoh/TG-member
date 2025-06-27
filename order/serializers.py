from rest_framework import serializers
from .models import Order

class OrderSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = ['user', 'price', 'created_at', 'updated_at']
