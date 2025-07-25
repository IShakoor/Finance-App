# Generated by Django 4.2.17 on 2025-07-03 20:20

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import encrypted_model_fields.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('banking', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', encrypted_model_fields.fields.EncryptedCharField()),
                ('amount', encrypted_model_fields.fields.EncryptedCharField(default='0.00')),
                ('date', models.DateField()),
                ('category', encrypted_model_fields.fields.EncryptedTextField(blank=True, null=True)),
                ('is_received', models.BooleanField(default=False)),
                ('transaction_id', models.CharField(max_length=255, unique=True)),
                ('bank_account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='banking.bankaccount')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
