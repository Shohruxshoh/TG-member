from django.db import transaction
from django.utils import timezone
from users.models import User
from balance.models import Balance, Transfer, Gift, GiftUsage, Buy, OrderBuy
from rest_framework import serializers


# Balance
class SBalanceUpdateSerializer(serializers.Serializer):
    amount = serializers.IntegerField()

    def validate_amount(self, value):
        if value == 0:
            raise serializers.ValidationError("The value cannot be 0.")
        return value


class SBalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Balance
        fields = ['balance']


class STransferSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transfer
        fields = ['id', 'receiver_email', 'value', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate(self, attrs):
        sender = self.context['request'].user
        receiver_email = attrs.get('receiver_email')
        value = attrs.get('value')

        if value <= 0:
            raise serializers.ValidationError("The value must be positive.")

        if sender.email == receiver_email:
            raise serializers.ValidationError("It is not possible to transfer to yourself.")

        if not User.objects.filter(email=receiver_email).exists():
            raise serializers.ValidationError("The recipient user was not found.")

        sender_balance = getattr(sender, 'user_balance', None)
        if not sender_balance or sender_balance.balance < value:
            raise serializers.ValidationError("You don't have enough funds in your balance.")

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


class STransferListSerializer(serializers.ModelSerializer):
    sign_value = serializers.SerializerMethodField()

    class Meta:
        model = Transfer
        fields = ["id", "sender", "receiver_email", "sign_value", "created_at"]

    def get_sign_value(self, obj):
        user = self.context["request"].user
        if user == obj.sender:
            return f"-{obj.value}"
        elif user.email == obj.receiver_email:
            return f"+{obj.value}"
        return str(obj.value)


class SGiftActivateSerializer(serializers.Serializer):
    gift = serializers.CharField(max_length=200)

    def validate(self, attrs):
        gift_code = attrs.get('gift')
        request = self.context['request']
        user = request.user

        try:
            gift = Gift.objects.get(gift=gift_code)
        except Gift.DoesNotExist:
            raise serializers.ValidationError("No such gift code exists.")

        # --- YANGI TEKSHIRUV ---
        now = timezone.now().date()

        if gift.expires_at:
            if not gift.is_active or gift.expires_at < now:
                raise serializers.ValidationError("This gift code is not active or has expired.")
        else:
            if not gift.is_active:
                raise serializers.ValidationError("This gift code is not active.")

        # Avval foydalanganmi
        if GiftUsage.objects.filter(user=user, gift=gift).exists():
            raise serializers.ValidationError("You have already used this gift code.")

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


class SGiftUsageSerializer(serializers.ModelSerializer):
    gift_value = serializers.CharField(source='gift.value')
    gift_code = serializers.CharField(source='gift.gift')

    class Meta:
        model = GiftUsage
        fields = ['id', 'gift_value', 'gift_code', 'used_at']


class SBuySerializers(serializers.ModelSerializer):
    class Meta:
        model = Buy
        fields = ['id', 'coin', 'price', 'self_uzs', 'self_rub', 'percent']


class SOrderBuySerializers(serializers.ModelSerializer):
    class Meta:
        model = OrderBuy
        fields = ['id', 'coin', 'price', 'is_paid', 'created_at']
