from django.db import models
from accounts.models import CustomUser
from app.models import Transaction
from django.utils.timezone import now
from django.core.validators import MinValueValidator
from decimal import Decimal


class Budget(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="budgets")
    name = models.CharField(max_length=255)
    current_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0,validators=[MinValueValidator(Decimal('0.00'))])
    target_amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    time_period = models.CharField(max_length=10, choices=[("weekly", "Weekly"), ("monthly", "Monthly"), ("annually", "Annually")])
    category = models.CharField(max_length=255)
    created_date = models.DateField(auto_now_add=True)
    last_reset_date = models.DateField(default=now)

    # find current amount
    def get_current_amount(self):
        all_transactions = Transaction.objects.filter(user=self.user)
        
        # filter transactions
        filtered_transactions = [
            t for t in all_transactions 
            if t.category == self.category and t.is_received == False
        ]

        # calc total spent
        total_spent = sum(abs(float(t.amount)) for t in filtered_transactions)
        return min(total_spent, self.target_amount)
    
    def save(self, *args, **kwargs):
        self.last_reset_date = now().date()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.target_amount}"