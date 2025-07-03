from django.core.exceptions import ValidationError
from django.db import models
from accounts.models.user import CustomUser
from encrypted_model_fields.fields import EncryptedTextField, EncryptedCharField

# class to manage transactions
class Transaction(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    bank_account = models.ForeignKey("app.BankAccount", on_delete=models.CASCADE)
    name = EncryptedCharField(max_length=255)
    amount = EncryptedCharField(max_length=10, default='0.00')
    date = models.DateField()
    category = EncryptedTextField(max_length=100, blank=True, null=True)
    is_received = models.BooleanField(default=False)
    transaction_id = models.CharField(max_length=255, unique=True)

    # prevent negative value amounts
    def clean(self):
        try:
            if float(self.amount) <= 0:
                raise ValidationError({'amount': 'Amount must be a positive value.'})
        except ValueError:
            raise ValidationError({'amount': 'Invalid amount value.'})

    # return info as string
    def __str__(self):
        return f"{self.name} - £{self.decrypted_amount:.2f} - {self.date}"
    
    @property
    def decrypted_amount(self):
        return float(self.amount)

    @decrypted_amount.setter
    def decrypted_amount(self, value):
        self.amount = str(value)