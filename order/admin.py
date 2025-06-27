from django.contrib import admin
from .models import Order

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'service_price', 'status', 'price', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username',)
    ordering = ('-created_at',)
