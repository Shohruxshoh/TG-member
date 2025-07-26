from django.contrib import admin
from .models import User, TelegramAccount

# Register your models here.
admin.site.register(User)
admin.site.register(TelegramAccount)

