from django.db import models
from accounts.models.user import CustomUser
from encrypted_model_fields.fields import EncryptedTextField, EncryptedCharField

# stores user bank account data
class BankAccount(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    bank_name = EncryptedCharField(max_length=255)
    account_name = EncryptedCharField(max_length=255, blank=True, null=True)
    account_id = EncryptedTextField(unique=True)
    account_type = models.CharField(max_length=50, choices=[('checking', 'Checking'), ('savings', 'Savings'), ('credit', 'Credit Card')])
    balance = EncryptedCharField(max_length=50, default='0.00')
    currency = models.CharField(max_length=10, default="GBP")
    last_synced = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} - {self.bank_name} ({self.account_type})"

    @property
    def decrypted_balance(self):
        return float(self.balance)

    @decrypted_balance.setter
    def decrypted_balance(self, value):
        self.balance = str(value)