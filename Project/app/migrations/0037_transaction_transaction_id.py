# Generated by Django 4.2.17 on 2025-03-29 10:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0036_alter_transaction_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='transaction_id',
            field=models.CharField(default=0, max_length=255, unique=True),
            preserve_default=False,
        ),
    ]
