from django.db import models


# Create your models here.

class DayOption(models.Model):
    day = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return str(self.day)


class Country(models.Model):
    name = models.CharField(max_length=200, unique=True)
    icon = models.CharField(max_length=255, null=True, blank=True)
    country_code = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Service(models.Model):
    CHOOSE_CATEGORY = (
        ("PREMIUM", 'Premium'),
        ("VIEW", 'View'),
        ("REACTION", 'Reaction'),
        ("MEMBER", 'Member'),
    )
    country = models.ForeignKey(Country, on_delete=models.PROTECT)
    category = models.CharField(max_length=20, choices=CHOOSE_CATEGORY, default="MEMBER", db_index=True)
    day = models.ForeignKey(DayOption, on_delete=models.SET_NULL, null=True)
    price = models.PositiveIntegerField(default=0)
    member = models.PositiveIntegerField(default=0)
    percent = models.PositiveIntegerField(default=0)
    post = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # agar percent > 0 bo‘lsa, narxni hisoblaymiz
        if self.percent > 0 and self.price > 0:
            discounted_price = self.price - (self.price * self.percent // 100)
            self.price = discounted_price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.country.name} - {self.category}"


class Link(models.Model):
    order = models.ForeignKey('order.Order', on_delete=models.CASCADE, related_name='channels')
    channel_name = models.CharField(max_length=200, null=True, blank=True)
    link = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.link
