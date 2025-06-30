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


class Balance(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_balance')
    balance = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} - {self.balance}"

    def perform_balance_update(self, amount):
        """
        Balansni xavfsiz tarzda yangilaydi. Transaction ichida bajariladi.
        """
        with transaction.atomic():
            # So'nggi qiymatni bazadan olib kelamiz (race condition ehtimoli uchun)
            self.refresh_from_db()

            new_balance = self.balance + int(amount)
            if new_balance < 0:
                raise ValueError("Balans manfiy bo‘lishi mumkin emas.")

            self.balance = new_balance
            self.save()
            return self.balance

    def perform_balance_subtraction_update(self, amount):
        """
        Balansni xavfsiz tarzda yangilaydi. Transaction ichida bajariladi.
        """
        with transaction.atomic():
            # So'nggi qiymatni bazadan olib kelamiz (race condition ehtimoli uchun)
            self.refresh_from_db()

            new_balance = self.balance - int(amount)
            if new_balance < 0:
                raise ValueError("Balans manfiy bo‘lishi mumkin emas.")

            self.balance = new_balance
            self.save()
            return self.balance
