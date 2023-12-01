from django.contrib import admin

from item.models import Item


@admin.register(Item)
class AdminItem(admin.ModelAdmin):
    list_display = ('id', 'description', 'name', 'price', 'currency',)
    list_filter = ('price', 'currency',)
    search_fields = ('id', 'name')
