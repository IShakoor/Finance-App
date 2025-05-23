# Generated by Django 4.2.17 on 2025-02-26 11:46

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import encrypted_model_fields.fields


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0014_alter_customuser_plaid_access_token'),
    ]

    operations = [
        migrations.CreateModel(
            name='BankAccount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bank_name', models.CharField(max_length=255)),
                ('account_name', models.CharField(blank=True, max_length=255, null=True)),
                ('account_id', encrypted_model_fields.fields.EncryptedTextField(unique=True)),
                ('account_type', models.CharField(choices=[('checking', 'Checking'), ('savings', 'Savings'), ('credit', 'Credit Card')], max_length=50)),
                ('balance', models.DecimalField(decimal_places=2, default=0.0, max_digits=12)),
                ('currency', models.CharField(default='GBP', max_length=10)),
                ('last_synced', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
