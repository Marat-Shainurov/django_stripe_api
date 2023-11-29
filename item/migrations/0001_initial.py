# Generated by Django 4.2.7 on 2023-11-29 18:39

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150, verbose_name='name')),
                ('description', models.TextField(verbose_name='description')),
                ('price', models.DecimalField(decimal_places=2, max_digits=15, verbose_name='price')),
            ],
            options={
                'verbose_name': 'Item',
                'verbose_name_plural': 'Items',
            },
        ),
    ]
