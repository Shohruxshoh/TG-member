from django.db import models

# Create your models here.

class Country(models.Model):
    name = models.CharField(max_length=200, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class ServicePrice(models.Model):
    CHOOSE_CATEGORY = (
        ("PREMIUM", 'Premium'),
        ("VIEW", 'View'),
        ("REACTION", 'Reaction'),
        ("MEMBER", 'Member'),
    )
    country = models.ForeignKey(Country, on_delete=models.PROTECT)
    category = models.CharField(max_length=20, choices=CHOOSE_CATEGORY, default="MEMBER", db_index=True)
    price = models.PositiveIntegerField(default=0)
    member = models.PositiveIntegerField(default=0)
    percent = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.country.name} - {self.category}"


class Link(models.Model):
    order = models.ForeignKey('order.Order', on_delete=models.CASCADE)
    link = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.link
