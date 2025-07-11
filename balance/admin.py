from django.contrib import admin

from balance.models import Balance, Transfer, Gift

# Register your models here.
admin.site.register(Balance)
admin.site.register(Transfer)
admin.site.register(Gift)
