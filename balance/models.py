from django.db import models
from django.db import transaction
import string
import random
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


class Transfer(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_transfers')
    receiver_email = models.EmailField(max_length=200)
    value = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.sender.username} → {self.receiver_email}: {self.value}"



class Gift(models.Model):
    gift = models.CharField(max_length=200, unique=True)
    value = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)  # yangi maydon
    expires_at = models.DateTimeField(null=True, blank=True)  # optional muddati
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def generate_random_gift(self, length=10):
        letters = string.ascii_uppercase + string.digits
        return ''.join(random.choices(letters, k=length))

    def save(self, *args, **kwargs):
        if not self.gift:
            self.gift = self.generate_random_gift()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.gift


class GiftUsage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    gift = models.ForeignKey(Gift, on_delete=models.CASCADE)
    used_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'gift']  # Har bir user faqat bir marta foydalansin

    def __str__(self):
        return f"{self.user.username} used {self.gift.gift}"
