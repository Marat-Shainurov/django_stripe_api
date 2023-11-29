from django.db import models

from item.models import Item, NULLABLE
from pricing.models.discount import Discount
from pricing.models.tax import Tax


class Order(models.Model):
    PAYMENT_STATUS = [
        ('in_progress', 'In_Progress'),
        ('paid', 'Paid'),
    ]

    items = models.ManyToManyField(Item, verbose_name='order_items', related_name='orders')
    tax = models.ForeignKey(Tax, verbose_name='order_tax', related_name='orders', on_delete=models.SET_NULL, **NULLABLE)
    discounts = models.ManyToManyField(Discount, verbose_name='order_discount', related_name='orders')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='created_at')
    total_price = models.DecimalField(default=0.0, decimal_places=2, max_digits=15, verbose_name='total_price')
    payment_status = models.CharField(
        verbose_name='payment_status', choices=PAYMENT_STATUS, default='in_progress', max_length=12)

    def __str__(self):
        return f'Order {self.pk} - {self.created_at}'

    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
