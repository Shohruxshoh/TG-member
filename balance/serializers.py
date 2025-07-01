from .models import Balance
from rest_framework import serializers


# Balance
class BalanceUpdateSerializer(serializers.Serializer):
    amount = serializers.IntegerField()

    def validate_amount(self, value):
        if value == 0:
            raise serializers.ValidationError("Qiymat 0 bo‘lishi mumkin emas.")
        return value


class BalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Balance
        fields = ['balance']
