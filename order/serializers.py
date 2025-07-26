from rest_framework import serializers

# from service.models import Link
# from service.serializers.app_serializers import SLinkSerializer
from .models import Order


class OrderSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = ['user', 'price', 'member', 'service_category', 'created_at', 'updated_at']


class OrderDetailSerializer(serializers.ModelSerializer):
    # links = serializers.SerializerMethodField()
    service = serializers.StringRelatedField()

    class Meta:
        model = Order
        fields = ['id', 'service', 'status', 'price', 'member', 'service_category', 'created_at'] # , 'links'

    # def get_links(self, obj):
    #     links = Link.objects.filter(order=obj)
    #     return SLinkSerializer(links, many=True).data
