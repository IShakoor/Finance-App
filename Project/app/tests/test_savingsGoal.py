from django.test import TestCase
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta
from app.models import SavingsGoal
from app.tests.factories import SavingsGoalFactory, UserFactory
from django.core.exceptions import ValidationError

# test for savings goal
class SavingsGoalModelTests(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.today = timezone.now().date()
        self.future_date = self.today + timedelta(days=30)
        
        self.savings_goal = SavingsGoalFactory(
            user=self.user,
            name="Vacation Fund",
            current_amount=Decimal('100.00'),
            target_amount=Decimal('1000.00'),
            goal_date=self.future_date
        )
    
    # test savings goal valid creation
    def test_savings_goal_creation(self):
        self.assertIsInstance(self.savings_goal, SavingsGoal)
        self.assertEqual(self.savings_goal.user, self.user)
        self.assertEqual(self.savings_goal.name, "Vacation Fund")
        self.assertEqual(self.savings_goal.current_amount, Decimal('100.00'))
        self.assertEqual(self.savings_goal.target_amount, Decimal('1000.00'))
        self.assertEqual(self.savings_goal.goal_date, self.future_date)
        self.assertIsNotNone(self.savings_goal.created_date)
    
    # test tostring
    def test_str_representation(self):
        expected_str = f"Vacation Fund - 1000.00"
        self.assertEqual(str(self.savings_goal), expected_str)

    # test deleting user cascades to goals
    def test_user_cascade_delete(self):
        goal_id = self.savings_goal.id
        self.user.delete()
        with self.assertRaises(SavingsGoal.DoesNotExist):
            SavingsGoal.objects.get(id=goal_id)
    
    # test user cannot set goal date earlier than current date
    def test_savings_goal_with_past_date(self):
        past_date = timezone.now().date() - timedelta(days=1)
        
        with self.assertRaises(ValidationError):
            goal = SavingsGoal(
                user=self.user,
                name="Past Date Goal",
                target_amount=Decimal('500.00'),
                goal_date=past_date
            )
            goal.full_clean()
    
    # test goal prevents negative target amount
    def test_savings_goal_with_negative_target_amount(self):
        with self.assertRaises(ValidationError):
            goal = SavingsGoal(
                user=self.user,
                name="Negative Goal",
                target_amount=Decimal('-500.00'),
                current_amount=Decimal('0.00'),
                goal_date=self.future_date
            )
            goal.full_clean()
    
    # test goal prevents negative current amount
    def test_savings_goal_with_negative_current_amount(self):
        with self.assertRaises(ValidationError):
            goal = SavingsGoal(
                user=self.user,
                name="Negative Current",
                target_amount=Decimal('500.00'),
                current_amount=Decimal('-100.00'),
                goal_date=self.future_date
            )
            goal.full_clean()
    
    # test goal without required fields
    def test_savings_goal_without_required_fields(self):
        with self.assertRaises(ValidationError):
            goal = SavingsGoal(
                user=self.user,
            )
            goal.full_clean()
    
    # test user can have multiple goals
    def test_multiple_savings_goals_for_same_user(self):
        goal2 = SavingsGoalFactory(
            user=self.user,
            name="New Car Fund"
        )
        self.assertIsInstance(goal2, SavingsGoal)
        self.assertEqual(SavingsGoal.objects.filter(user=self.user).count(), 2)
    
    # test differnet users with same goal
    def test_savings_goals_for_different_users(self):
        user2 = UserFactory()
        
        goal2 = SavingsGoalFactory(
            user=user2,
            name="Vacation Fund"
        )
        self.assertIsInstance(goal2, SavingsGoal)
        self.assertEqual(SavingsGoal.objects.filter(name="Vacation Fund").count(), 2)
            
    # tets goal created date assigned automatically
    def test_savings_goal_created_date_auto_set(self):
        now = timezone.now()
        
        goal = SavingsGoal.objects.create(
            user=self.user,
            name="Auto Date Goal",
            target_amount=Decimal('500.00'),
            goal_date=self.future_date
        )
        self.assertLessEqual((timezone.now() - goal.created_date).total_seconds(), 5)
    
    # create goal with same target and current amount
    def test_savings_goal_with_current_amount_equal_to_target(self):
        goal = SavingsGoalFactory(
            user=self.user,
            current_amount=Decimal('1000.00'),
            target_amount=Decimal('1000.00')
        )
        self.assertEqual(goal.current_amount, goal.target_amount)
    
    # test current amount > target
    def test_savings_goal_with_current_amount_greater_than_target(self):
        goal = SavingsGoal(
            user=self.user,
            name="Exceeded Goal",
            current_amount=Decimal('1500.00'),
            target_amount=Decimal('1000.00'),
            goal_date=self.future_date
        )
        goal.full_clean()
        goal.save()
        self.assertGreater(goal.current_amount, goal.target_amount)