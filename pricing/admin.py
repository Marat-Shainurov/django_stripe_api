from django.contrib import admin

from pricing.models.discount import Discount
from pricing.models.tax import Tax


@admin.register(Discount)
class AdminDiscount(admin.ModelAdmin):
    list_display = ('id', 'name', 'amount_off', 'percent_off')
    list_filter = ('amount_off', 'percent_off')
    search_fields = ('id', 'name',)


@admin.register(Tax)
class AdminTax(admin.ModelAdmin):
    list_display = ('id', 'name', 'rate',)
    list_filter = ('rate',)
    search_fields = ('id', 'name',)
