from django.db import models


class Tax(models.Model):
    name = models.CharField(verbose_name='tax_name', max_length=150, unique=True)
    rate = models.DecimalField(verbose_name='tax_rate', max_digits=5, decimal_places=2)

    def __str__(self):
        return f'Tax "{self.name}"'

    class Meta:
        verbose_name = 'Tax'
        verbose_name_plural = 'Taxes'
