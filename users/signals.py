from balance.models import Balance
from .models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save , sender = User)
def  create_profile(sender, instance, created, **kwargs):
    if created:
        Balance.objects.create(user=instance)