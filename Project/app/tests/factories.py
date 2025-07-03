import factory
import random
import uuid
from app.models import *
from accounts.models.user import CustomUser

# factory for the user model
class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CustomUser
        django_get_or_create = ('email',)

    username = factory.Faker("user_name")
    email = factory.Faker("email")
    password = factory.PostGenerationMethodCall("set_password", "Password123!")
    is_staff = False
    is_active = True
    is_verified = True
    plaid_access_token = factory.Faker("uuid4")

# factory for the BankAccount model
class BankAccountFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = BankAccount
        django_get_or_create = ('account_id',)

    user = factory.SubFactory(UserFactory)
    bank_name = factory.Faker("company")
    account_name = factory.Faker("word")
    account_id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    account_type = factory.Iterator(['checking', 'savings', 'credit'])
    balance = factory.LazyFunction(lambda: str(round(random.uniform(100, 10000), 2)))
    currency = "GBP"
    is_active = True

# factory for the transaction model
class TransactionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Transaction
        django_get_or_create = ('transaction_id',)

    user = factory.SubFactory(UserFactory)
    bank_account = factory.SubFactory(BankAccountFactory, user=factory.SelfAttribute('..user'))
    name = factory.Faker("sentence", nb_words=3)
    amount = factory.LazyFunction(lambda: str(round(random.uniform(10, 1000), 2)))
    date = factory.Faker("date_this_decade")
    category = factory.Iterator(['Food and Drink', 'Travel', 'Recreation', 'Transfer', 'Shops'])
    is_received = factory.Faker("boolean")
    transaction_id = factory.LazyFunction(lambda: str(uuid.uuid4()))

# factory for the budget model
class BudgetFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Budget
    
    user = factory.SubFactory(UserFactory)
    name = factory.Faker("word")
    current_amount = factory.LazyFunction(lambda: round(random.uniform(10, 500), 2))
    target_amount = factory.LazyFunction(lambda: round(random.uniform(500, 2000), 2))
    time_period = factory.Iterator(["weekly", "monthly", "annually"])
    category = factory.Iterator(['Food and Drink', 'Travel', 'Recreation', 'Transfer', 'Shops'])
    created_date = factory.Faker("date_this_decade")

# factory for the savings model
class SavingsGoalFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SavingsGoal

    user = factory.SubFactory(UserFactory)
    name = factory.Faker("word")
    current_amount = factory.LazyFunction(lambda: round(random.uniform(10, 500), 2))
    target_amount = factory.LazyFunction(lambda: round(random.uniform(500, 2000), 2))
    goal_date = factory.Faker("date_between", start_date="+1d", end_date="+3y")

# factory for the message model
class MessageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Message

    user = factory.SubFactory(UserFactory)
    title = factory.Faker("word")
    content = factory.Faker("paragraph")
    is_read = factory.Faker("boolean", chance_of_getting_true=25)