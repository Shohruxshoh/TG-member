from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.password_validation import validate_password
from .models import User, Balance
from rest_framework import serializers
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from dotenv import load_dotenv
import os

load_dotenv()

EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'password']

    def create(self, validated_data):
        return User.objects.create_user(username=validated_data['email'], **validated_data)


class RegisterGoogleSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email']

    def create(self, validated_data):
        return User.objects.create_user(username=validated_data['email'], **validated_data)


class LoginGoogleSerializer(serializers.Serializer):
    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)
    email = serializers.EmailField(write_only=True)

    def validate(self, attrs):
        email = attrs.get("email")
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Bunday foydalanuvchi mavjud emas.")

        refresh = RefreshToken.for_user(user)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }


class PasswordChangeSerializer(serializers.Serializer):
    password1 = serializers.CharField(write_only=True, style={'input_type': 'password'}, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, style={'input_type': 'password'})

    def validate(self, attrs):
        if attrs['password1'] != attrs['password2']:
            raise serializers.ValidationError({'password2': 'Parollar mos emas.'})
        return attrs


class PasswordResetEmailRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Bunday email ro'yxatda mavjud emas.")
        return value

    def save(self, request):
        email = self.validated_data['email']
        user = User.objects.get(email=email)

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        reset_url = f"http://127.0.0.1:8000/api/users/reset-password/{uid}/{token}/"

        send_mail(
            subject="Parolni tiklash",
            message=f"Parolni tiklash uchun ushbu havolaga o‘ting: {reset_url}",
            from_email=EMAIL_HOST_USER,
            recipient_list=[email],
        )


class PasswordResetConfirmSerializer(serializers.Serializer):
    uidb64 = serializers.CharField()
    token = serializers.CharField()
    password1 = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)

    def validate(self, attrs):
        try:
            uid = urlsafe_base64_decode(attrs['uidb64']).decode()
            user = User.objects.get(pk=uid)
        except Exception:
            raise serializers.ValidationError("Noto'g'ri token yoki foydalanuvchi.")

        if not default_token_generator.check_token(user, attrs['token']):
            raise serializers.ValidationError("Token noto'g'ri yoki muddati tugagan.")

        if attrs['password1'] != attrs['password2']:
            raise serializers.ValidationError("Parollar mos emas.")

        attrs['user'] = user
        return attrs

    def save(self):
        user = self.validated_data['user']
        user.set_password(self.validated_data['password1'])
        user.save()


class UserSerializer(serializers.ModelSerializer):
    balance = serializers.IntegerField(read_only=True)
    class Meta:
        model = User
        fields = ['email', 'balance']



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
