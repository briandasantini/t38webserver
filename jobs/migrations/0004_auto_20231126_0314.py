# Generated by Django 3.2.13 on 2023-11-26 03:14

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0003_auto_20231125_2238'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cpep',
            name='cutoff',
            field=models.FloatField(blank=True, default=6.0),
        ),
        migrations.AlterField(
            model_name='cpep',
            name='motif',
            field=models.IntegerField(blank=True, default=5, validators=[django.core.validators.MaxValueValidator(7), django.core.validators.MinValueValidator(4)]),
        ),
    ]
