from django.contrib import admin

from item.models import Item


@admin.register(Item)
class AdminItem(admin.ModelAdmin):
    list_display = ('id', 'description', 'name', 'price',)
    list_filter = ('price',)
    search_fields = ('id', 'name')
