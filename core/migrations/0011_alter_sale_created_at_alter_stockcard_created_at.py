# Generated by Django 5.0.2 on 2024-03-08 09:00

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_alter_stockcard_created_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sale',
            name='created_at',
            field=models.DateField(default=datetime.datetime(2024, 3, 8, 12, 0, 53, 402044)),
        ),
        migrations.AlterField(
            model_name='stockcard',
            name='created_at',
            field=models.DateField(default=datetime.datetime(2024, 3, 8, 12, 0, 53, 401534)),
        ),
    ]
