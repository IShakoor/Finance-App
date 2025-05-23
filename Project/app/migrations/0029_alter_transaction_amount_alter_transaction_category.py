# Generated by Django 4.2.17 on 2025-03-05 11:42

from django.db import migrations
import encrypted_model_fields.fields


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0028_alter_transaction_amount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='amount',
            field=encrypted_model_fields.fields.EncryptedCharField(default='0.00'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='category',
            field=encrypted_model_fields.fields.EncryptedTextField(blank=True, null=True),
        ),
    ]
