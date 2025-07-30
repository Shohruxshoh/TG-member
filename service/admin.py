from django.contrib import admin
from .models import Country, Service, DayOption


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at')
    search_fields = ('name',)


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'country', 'category', 'price', 'member', 'percent')
    list_filter = ('country', 'category')
    search_fields = ('category',)

admin.site.register(DayOption)

# @admin.register(Link)
# class LinkAdmin(admin.ModelAdmin):
#     list_display = ('id', 'order', 'link', 'created_at')
#     search_fields = ('link',)
