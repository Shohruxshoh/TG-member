from django.contrib import admin
from .models import Order, OrderMember


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'service', 'status', 'price', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username',)
    ordering = ('-created_at',)


@admin.register(OrderMember)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'telegram', 'order', 'joined_at', 'is_active', 'member_duration')
    list_filter = ('is_active',)
    search_fields = ('user__username',)
    ordering = ('-joined_at',)
# admin.site.register(OrderMember)
