# Generated by Django 4.2.17 on 2025-03-02 11:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0018_remove_bankaccount_balance_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bankaccount',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]
