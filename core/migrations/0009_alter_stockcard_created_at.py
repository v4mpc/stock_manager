# Generated by Django 5.0.2 on 2024-03-08 08:53

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_product_active'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stockcard',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 3, 8, 11, 53, 51, 717098)),
        ),
    ]
