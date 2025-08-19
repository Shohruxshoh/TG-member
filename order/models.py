from decimal import Decimal
from django.db import models
from django.db.models import Count, F, Value, Case, When, ExpressionWrapper
from django.db.models import DecimalField
from order.enums import Status
from service.models import Service
from users.models import User, TelegramAccount


# Create your models here.
class OrderQuerySet(models.QuerySet):
    def with_totals(self):
        """
        DB darajasida ikki annotation:
        - total_members_anno: members count
        - calculated_total: (member / price) * total_members_anno
          => price=0 bo'lsa 0
        """
        qs = self.annotate(
            total_members_anno=Count('members', distinct=True)
        )
        qs = qs.annotate(
            calculated_total=Case(
                When(
                    price__gt=0,
                    then=ExpressionWrapper(
                        (F('price') / F('member')) / F('total_members_anno'),
                        output_field=DecimalField(max_digits=20, decimal_places=2)
                    )
                ),
                default=Value(0),
                output_field=DecimalField(max_digits=20, decimal_places=2)
            )
        )
        return qs


class OrderManager(models.Manager.from_queryset(OrderQuerySet)):
    pass


class Order(models.Model):
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    link = models.CharField(max_length=200)
    channel_name = models.CharField(max_length=200)
    channel_id = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    member = models.PositiveIntegerField(default=0)
    service_category = models.CharField(max_length=200, null=True, blank=True, db_index=True)
    country_code = models.CharField(max_length=200, null=True, blank=True, db_index=True)
    day = models.PositiveIntegerField(default=0)
    number_added = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = OrderManager()

    class Meta:
        indexes = [
            models.Index(fields=['status', 'is_active']),
            models.Index(fields=['is_active', 'created_at']),
        ]

    def __str__(self):
        return f"Order#{self.pk} by {self.user}"

    @property
    def self_members(self):
        """Related OrderMember yozuvlari soni."""
        return self.members.count()

    @property
    def calculated_total(self):
        """
        Python darajasida fallback:
        (member / price) * self_members
        price=0 -> 0
        """
        if not self.price:
            return Decimal('0')
        return (Decimal(self.price) / Decimal(self.member)) * Decimal(self.self_members)


class OrderMember(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='members')
    telegram = models.ForeignKey(TelegramAccount, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    vip = models.PositiveIntegerField(default=0)
    member_duration = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['order', 'user', 'telegram']),
            models.Index(fields=['user', 'telegram', 'joined_at']),
        ]

    def __str__(self):
        return f"{self.user.email}- {self.order.channel_name}"
