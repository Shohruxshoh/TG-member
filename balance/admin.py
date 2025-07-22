from django.contrib import admin

from balance.models import Balance, Transfer, Gift, Buy, OrderBuy

# Register your models here.
admin.site.register(Balance)
admin.site.register(Transfer)
admin.site.register(Gift)
admin.site.register(Buy)
admin.site.register(OrderBuy)
