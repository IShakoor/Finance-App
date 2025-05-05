from django.test import TestCase
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta
from app.models import Budget
from app.tests.factories import BudgetFactory, UserFactory, TransactionFactory
from django.core.exceptions import ValidationError

# tests for budget model
class BudgetModelTests(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.budget = BudgetFactory(
            user=self.user,
            name="Test Budget",
            current_amount=Decimal('0.00'),
            target_amount=Decimal('500.00'),
            time_period="monthly",
            category="Food and Drink"
        )
        
        # testing transactions
        self.transaction1 = TransactionFactory(
            user=self.user,
            amount="-50.00",
            category="Food and Drink",
            is_received=False
        )
        
        self.transaction2 = TransactionFactory(
            user=self.user,
            amount="-30.00",
            category="Food and Drink",
            is_received=False
        )
        
        self.transaction3 = TransactionFactory(
            user=self.user,
            amount="-100.00",
            category="Travel",
            is_received=False
        )
        
        self.transaction4 = TransactionFactory(
            user=self.user,
            amount="20.00",
            category="Food and Drink",
            is_received=True 
        )
    
    # create valid budget
    def test_budget_creation(self):
        self.assertIsInstance(self.budget, Budget)
        self.assertEqual(self.budget.user, self.user)
        self.assertEqual(self.budget.name, "Test Budget")
        self.assertEqual(self.budget.current_amount, Decimal('0.00'))
        self.assertEqual(self.budget.target_amount, Decimal('500.00'))
        self.assertEqual(self.budget.time_period, "monthly")
        self.assertEqual(self.budget.category, "Food and Drink")
        self.assertIsNotNone(self.budget.created_date)
        self.assertIsNotNone(self.budget.last_reset_date)
    
    # test tostring
    def test_str_representation(self):
        expected_str = f"Test Budget - 500.00"
        self.assertEqual(str(self.budget), expected_str)
    
    # test get curret amount
    def test_get_current_amount(self):
        expected_amount = abs(float(self.transaction1.amount)) + abs(float(self.transaction2.amount))
        self.assertEqual(self.budget.get_current_amount(), expected_amount)
    
    # test current amount - no transactions
    def test_get_current_amount_with_no_transactions(self):
        budget = BudgetFactory(
            user=self.user,
            category="Entertainment"
        )
        self.assertEqual(budget.get_current_amount(), 0)
    
    # test get current amount - spending > target
    def test_get_current_amount_exceeds_target(self):
        budget = BudgetFactory(
            user=self.user,
            target_amount=Decimal('10.00'),
            category="Food and Drink"
        )
        
        self.assertEqual(budget.get_current_amount(), 10.00)
    
    # test save sets reset date to today
    def test_save_method_sets_last_reset_date(self):
        today = timezone.now().date()
        self.budget.last_reset_date = today - timedelta(days=30)
        self.budget.save()
        self.assertEqual(self.budget.last_reset_date, today)
    
    # test deleting user deletes budget
    def test_user_cascade_delete(self):
        budget_id = self.budget.id
        self.user.delete()
        with self.assertRaises(Budget.DoesNotExist):
            Budget.objects.get(id=budget_id)
    
    # test invalid time period
    def test_budget_with_invalid_time_period(self):
        with self.assertRaises(ValidationError):
            budget = Budget(
                user=self.user,
                name="Invalid Budget",
                target_amount=Decimal('500.00'),
                time_period="quarterly",
                category="Food and Drink"
            )
            budget.full_clean()
    
    # test budget negative target amount
    def test_budget_with_negative_target_amount(self):
        with self.assertRaises(ValidationError):
            budget = Budget(
                user=self.user,
                name="Negative Budget",
                target_amount=Decimal('-500.00'),
                time_period="monthly",
                category="Food and Drink"
            )
            budget.full_clean()
    
    # test budget without required fields
    def test_budget_without_required_fields(self):
        with self.assertRaises(ValidationError):
            budget = Budget(
                user=self.user,
            )
            budget.full_clean()
    
    # test different users can have same budget
    def test_budget_for_different_users(self):
        user2 = UserFactory()
        
        budget2 = BudgetFactory(
            user=user2,
            name="Test Budget",
            category="Food and Drink"
        )
        
        self.assertIsInstance(budget2, Budget)
        self.assertEqual(Budget.objects.filter(name="Test Budget").count(), 2)
    
    # test curren amount with multiple users
    def test_get_current_amount_with_multiple_users(self):
        user2 = UserFactory()
        
        TransactionFactory(
            user=user2,
            amount="-200.00",
            category="Food and Drink",
            is_received=False
        )
        
        expected_amount = abs(float(self.transaction1.amount)) + abs(float(self.transaction2.amount))
        self.assertEqual(self.budget.get_current_amount(), expected_amount)
    
    # test budget create date auto assigned
    def test_budget_created_date_auto_set(self):
        today = timezone.now().date()

        budget = Budget.objects.create(
            user=self.user,
            name="Auto Date Budget",
            target_amount=Decimal('500.00'),
            time_period="monthly",
            category="Food and Drink"
        )
        
        self.assertEqual(budget.created_date, today)