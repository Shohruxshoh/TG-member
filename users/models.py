from django.contrib.auth.models import AbstractUser
from django.db import models
from rest_framework_simplejwt.tokens import RefreshToken
from django.db import transaction


# Create your models here.
class User(AbstractUser):
    email = models.EmailField(unique=True, db_index=True)

    def __str__(self):
        return self.email

    def get_tokens(self):
        """Returns the tokens for the user."""
        refresh = RefreshToken.for_user(self)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }

    @property
    def balance(self):
        return self.user_balance.balance


class TelegramAccount(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='telegram_accounts')
    telegram_id = models.CharField(max_length=200, unique=True, db_index=True)
    phone_number = models.CharField(max_length=200, unique=True)
    country_code = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        indexes = [
            models.Index(fields=["telegram_id", "is_active"]),  # tezkor qidiruv uchun composite index
        ]

    def __str__(self):
        return str(self.telegram_id)
