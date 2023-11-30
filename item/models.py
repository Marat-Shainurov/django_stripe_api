from django.db import models

NULLABLE = {'blank': True, 'null': True}


class Item(models.Model):
    CURRENCY = {
        ('rub', 'RUB'),
        ('usd', 'USD')
    }

    name = models.CharField(verbose_name='name', max_length=150)
    description = models.TextField(verbose_name='description')
    price = models.DecimalField(verbose_name='price', max_digits=15, decimal_places=2)
    currency = models.CharField(choices=CURRENCY, verbose_name='price_currency', default='rub')

    def __str__(self):
        return f'Item "{self.name}"'

    class Meta:
        verbose_name = 'Item'
        verbose_name_plural = 'Items'
