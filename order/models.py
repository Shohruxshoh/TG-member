from django.db import models

from service.models import Service
from users.models import User


# Create your models here.

class Order(models.Model):
    CHOOSE_STATUS = (
        ("PENDING", 'Pending'),
        ("COMPLETED", 'Completed'),
        ("FAILED", 'Failed'),
    )
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True, db_index=True)
    status = models.CharField(max_length=20, choices=CHOOSE_STATUS, default="PENDING")
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    price = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.user)

