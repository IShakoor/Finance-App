# Generated by Django 4.2.17 on 2025-03-22 14:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0033_remove_transaction_unique_user_transaction_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='budget',
            name='current_amount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
    ]
