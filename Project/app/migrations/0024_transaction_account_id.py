# Generated by Django 4.2.17 on 2025-03-05 10:53

from django.db import migrations
import encrypted_model_fields.fields


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0023_alter_transaction_amount_alter_transaction_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='account_id',
            field=encrypted_model_fields.fields.EncryptedCharField(blank=True, null=True),
        ),
    ]
