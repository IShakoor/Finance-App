# Generated by Django 4.2.17 on 2025-01-08 17:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_transaction_source_alter_transaction_date'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='transaction',
            name='source',
        ),
        migrations.AddField(
            model_name='transaction',
            name='is_received',
            field=models.BooleanField(default=False),
        ),
    ]
