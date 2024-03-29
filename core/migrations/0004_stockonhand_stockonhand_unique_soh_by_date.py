# Generated by Django 5.0.2 on 2024-03-03 17:41

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_alter_stockcard_product'),
    ]

    operations = [
        migrations.CreateModel(
            name='StockOnHand',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.FloatField()),
                ('created_at', models.DateField()),
                ('updated_at', models.DateField(auto_now=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='core.product')),
            ],
            options={
                'db_table': 'stock_on_hand',
                'ordering': ['-id'],
                'indexes': [models.Index(fields=['product', 'created_at'], name='stock_on_ha_product_3477ee_idx')],
            },
        ),
        migrations.AddConstraint(
            model_name='stockonhand',
            constraint=models.UniqueConstraint(fields=('product', 'created_at'), name='unique soh by date'),
        ),
    ]
