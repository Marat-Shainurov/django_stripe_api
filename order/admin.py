from django.contrib import admin

from order.models import Order


@admin.register(Order)
class AdminItem(admin.ModelAdmin):
    list_display = ('id', 'payment_status', 'total_price', 'created_at',)
    list_filter = ('payment_status',)
    search_fields = ('id',)
