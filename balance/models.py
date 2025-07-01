from django.db import models
from django.db import transaction

from users.models import User


# Create your models here.
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
