# Generated by Django 5.1.5 on 2025-04-01 15:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("cart", "0008_alter_productquantity_total_price"),
    ]

    operations = [
        migrations.AlterField(
            model_name="productquantity",
            name="total_price",
            field=models.DecimalField(
                blank=True, decimal_places=2, max_digits=10, null=True
            ),
        ),
    ]
