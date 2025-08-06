from django.contrib import admin

from balance.models import Balance, Transfer, Gift, Buy, OrderBuy, GiftUsage, Vip, Currency

# Register your models here.
admin.site.register(Balance)
admin.site.register(Transfer)
admin.site.register(Gift)
admin.site.register(GiftUsage)
admin.site.register(Buy)
admin.site.register(OrderBuy)
admin.site.register(Vip)
admin.site.register(Currency)
