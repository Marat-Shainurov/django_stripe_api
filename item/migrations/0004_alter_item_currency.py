# Generated by Django 4.2.7 on 2023-12-02 19:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('item', '0003_alter_item_currency'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='currency',
            field=models.CharField(choices=[('eur', 'EUR'), ('rub', 'RUB')], default='rub', verbose_name='price_currency'),
        ),
    ]
