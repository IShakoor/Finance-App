# Generated by Django 4.2.17 on 2025-02-26 17:43

from django.db import migrations
import encrypted_model_fields.fields


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0016_alter_bankaccount_account_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bankaccount',
            name='account_id',
            field=encrypted_model_fields.fields.EncryptedTextField(unique=True),
        ),
    ]
