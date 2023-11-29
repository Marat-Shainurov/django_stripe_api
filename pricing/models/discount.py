from django.db import models


class Discount(models.Model):
    name = models.CharField(verbose_name='discount_name', max_length=150, unique=True)
    amount = models.DecimalField(verbose_name='discount_amount', max_digits=10, decimal_places=2)

    def __str__(self):
        return f'Discount "{self.name}"'

    class Meta:
        verbose_name = 'Discount'
        verbose_name_plural = 'Discounts'
