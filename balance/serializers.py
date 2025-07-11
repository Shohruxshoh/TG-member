from django.db import transaction
from django.utils import timezone

from users.models import User
from .models import Balance, Transfer, Gift, GiftUsage
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


class TransferSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transfer
        fields = ['id', 'receiver_email', 'value', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate(self, attrs):
        sender = self.context['request'].user
        receiver_email = attrs.get('receiver_email')
        value = attrs.get('value')

        if value <= 0:
            raise serializers.ValidationError("Qiymat musbat bo'lishi kerak.")

        if sender.email == receiver_email:
            raise serializers.ValidationError("O'zingizga transfer qilish mumkin emas.")

        if not User.objects.filter(email=receiver_email).exists():
            raise serializers.ValidationError("Qabul qiluvchi foydalanuvchi topilmadi.")

        sender_balance = getattr(sender, 'user_balance', None)
        if not sender_balance or sender_balance.balance < value:
            raise serializers.ValidationError("Balansingizda yetarli mablag' yo'q.")

        return attrs

    def create(self, validated_data):
        sender = self.context['request'].user
        receiver = User.objects.get(email=validated_data['receiver_email'])
        value = validated_data['value']

        sender_balance = sender.user_balance
        receiver_balance, _ = Balance.objects.get_or_create(user=receiver)

        with transaction.atomic():
            sender_balance.perform_balance_subtraction_update(value)
            receiver_balance.perform_balance_update(value)

            transfer = Transfer.objects.create(
                sender=sender,
                receiver_email=receiver.email,
                value=value
            )
        return transfer
class GiftActivateSerializer(serializers.Serializer):
    gift = serializers.CharField(max_length=200)

    def validate(self, attrs):
        gift_code = attrs.get('gift')
        request = self.context['request']
        user = request.user

        try:
            gift = Gift.objects.get(gift=gift_code)
        except Gift.DoesNotExist:
            raise serializers.ValidationError("Bunday gift kodi mavjud emas.")

        # --- YANGI TEKSHIRUV ---
        now = timezone.now()

        if gift.expires_at:
            if not gift.is_active or gift.expires_at < now:
                raise serializers.ValidationError("Bu gift kodi aktiv emas yoki muddati tugagan.")
        else:
            if not gift.is_active:
                raise serializers.ValidationError("Bu gift kodi aktiv emas.")

        # Avval foydalanganmi
        if GiftUsage.objects.filter(user=user, gift=gift).exists():
            raise serializers.ValidationError("Bu gift kodni allaqachon ishlatgansiz.")

        attrs['gift'] = gift
        return attrs

    def save(self, **kwargs):
        user = self.context['request'].user
        gift = self.validated_data['gift']

        with transaction.atomic():
            balance, _ = Balance.objects.get_or_create(user=user)
            balance.perform_balance_update(gift.value)

            GiftUsage.objects.create(user=user, gift=gift)

        return gift
