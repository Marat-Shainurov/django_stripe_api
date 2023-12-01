from django.core.exceptions import ValidationError
from django.db import models

from item.models import NULLABLE


class Discount(models.Model):
    name = models.CharField(verbose_name='discount_name', max_length=150, unique=True)
    amount_off = models.DecimalField(verbose_name='discount_amount', max_digits=10, decimal_places=2, **NULLABLE)
    percent_off = models.DecimalField(verbose_name='discount_percentage', max_digits=5, decimal_places=2, **NULLABLE)

    def __str__(self):
        return f'Discount "{self.name}"'

    class Meta:
        verbose_name = 'Discount'
        verbose_name_plural = 'Discounts'

    def clean(self):
        if self.percent_off and self.amount_off:
            raise ValidationError('Either percent_off or amount_off should be specified, not both.')

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
