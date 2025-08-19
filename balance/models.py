from django.db import models
from django.db import transaction
import string
import random

from balance.enums import Currency
from service.enums import Category
from users.models import User
from django.db.models import F


# Create your models here.
class Balance(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_balance')
    balance = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} - {self.balance}"

    def perform_balance_update(self, amount):
        if int(amount) < 0:
            raise ValueError("Cannot add a negative value.")

        with transaction.atomic():
            updated = Balance.objects.filter(
                pk=self.pk
            ).update(balance=F('balance') + int(amount))

            if not updated:
                raise ValueError("Balance update error.")

            self.refresh_from_db()
            return self.balance

    def perform_balance_subtraction_update(self, amount):
        amount = int(amount)
        with transaction.atomic():
            self.refresh_from_db()

            if self.balance < amount:
                raise ValueError("Insufficient balance.")

            updated = Balance.objects.filter(
                pk=self.pk
            ).update(balance=F('balance') - amount)

            if not updated:
                raise ValueError("Balance update error.")

            self.refresh_from_db()
            return self.balance


class Transfer(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_transfers', db_index=True)
    receiver_email = models.EmailField(max_length=200)
    value = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.sender.username} → {self.receiver_email}: {self.value}"

    def display_for_user(self, user):
        """
        Berilgan user uchun transferni ko‘rsatadi.
        Yuboruvchi uchun '-' belgisi, qabul qiluvchi uchun '+' belgisi qo‘yiladi.
        """
        if user == self.sender:
            return f"-{self.value}"
        elif user.email == self.receiver_email:
            return f"+{self.value}"
        return str(self.value)  # boshqa odam uchun oddiy ko‘rsatish


class Gift(models.Model):
    gift = models.CharField(max_length=200, unique=True)
    value = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)  # yangi maydon
    expires_at = models.DateField(null=True, blank=True)  # optional muddati
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
        indexes = [
            models.Index(fields=["user", "gift"]),
        ]

    def __str__(self):
        return f"{self.user.username} used {self.gift.gift}"


class Buy(models.Model):
    coin = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    percent = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # agar percent > 0 bo‘lsa, narxni hisoblaymiz
        if self.percent > 0 and self.price > 0:
            discounted_price = self.price - (self.price * self.percent / 100)
            self.price = discounted_price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Coin: {self.coin}- Price: {self.price}"


class OrderBuy(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    buy = models.ForeignKey(Buy, on_delete=models.PROTECT)
    coin = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_paid = models.BooleanField(default=False)
    currency = models.CharField(max_length=10, choices=Currency.choices, default=Currency.DOLLAR)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Coin: {self.coin}- Price: {self.price}"


class Vip(models.Model):
    vip = models.PositiveIntegerField(default=0)
    category = models.CharField(max_length=20, choices=Category.choices, default=Category.MEMBER, db_index=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.category


class Currency(models.Model):
    som = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    rubli = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"So'm: {self.som}- rubli: {self.rubli}"
