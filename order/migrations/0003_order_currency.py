# Generated by Django 4.2.7 on 2023-12-01 17:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0002_remove_order_discounts_order_discount'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='currency',
            field=models.CharField(blank=True, max_length=3, null=True, verbose_name='currency'),
        ),
    ]
