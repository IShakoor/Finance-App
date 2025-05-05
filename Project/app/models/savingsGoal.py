from django.db import models
from app.models import CustomUser
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.utils import timezone
from django.core.exceptions import ValidationError

def validate_future_date(value):
    if value < timezone.now().date():
        raise ValidationError("Goal date cannot be in the past.")
        
class SavingsGoal(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="savings_goals")
    name = models.CharField(max_length=255)
    target_amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    current_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, validators=[MinValueValidator(Decimal('0.00'))])
    goal_date = models.DateField(validators=[validate_future_date])
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.target_amount}"