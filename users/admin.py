from django.contrib import admin
from .models import User, TelegramAccount

# Register your models here.
# admin.site.register(User)
admin.site.register(TelegramAccount)
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'email']
    search_fields = ['email']
