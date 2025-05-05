from django.test import TestCase
from app.models import BankAccount
from app.tests.factories import UserFactory, BankAccountFactory

# transaction models test
class BankAccountTests(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.bank_account = BankAccountFactory(user=self.user)

    # test valid creation
    def test_bank_account_creation(self):
        self.assertIsInstance(self.bank_account, BankAccount)
        self.assertEqual(self.bank_account.user, self.user)
        self.assertTrue(self.bank_account.is_active)
        self.assertIsNotNone(self.bank_account.last_synced)
    
    # test tostring func
    def test_str_representation(self):
        expected_str = f"{self.user.username} - {self.bank_account.bank_name} ({self.bank_account.account_type})"
        self.assertEqual(str(self.bank_account), expected_str)
    
    # test decryption
    def test_decrypted_balance_property(self):
        self.bank_account.balance = "123.45"
        self.bank_account.save()
        self.assertEqual(self.bank_account.decrypted_balance, 123.45)
        self.assertIsInstance(self.bank_account.decrypted_balance, float)
    
    # test encryption
    def test_decrypted_balance_setter(self):
        self.bank_account.decrypted_balance = 567.89
        self.bank_account.save()
        self.assertEqual(self.bank_account.balance, "567.89")
        self.assertEqual(self.bank_account.decrypted_balance, 567.89)

    # test account types  
    def test_account_type_choices(self):
        valid_types = ['checking', 'savings', 'credit']
        for account_type in valid_types:
            account = BankAccountFactory(account_type=account_type)
            self.assertEqual(account.account_type, account_type)
    
    # check last_synced updates automatically
    def test_last_synced_auto_update(self):
        old_sync_time = self.bank_account.last_synced
        import time
        time.sleep(0.1)
        self.bank_account.bank_name = "Updated Bank Name"
        self.bank_account.save()
        self.assertGreater(self.bank_account.last_synced, old_sync_time)
    
    # test cascade delete
    def test_cascade_delete(self):
        account_id = self.bank_account.id
        self.user.delete()
        with self.assertRaises(BankAccount.DoesNotExist):
            BankAccount.objects.get(id=account_id)
    
    # test default currency
    def test_default_currency(self):
        self.assertEqual(self.bank_account.currency, "GBP")
        account = BankAccountFactory(currency="USD")
        self.assertEqual(account.currency, "USD")
    
    # test sensitive fields are correctly encrypted
    def test_encrypted_fields(self):
        test_bank_name = "Secret Bank"
        test_account_name = "Secret Account"
        self.bank_account.bank_name = test_bank_name
        self.bank_account.account_name = test_account_name
        self.bank_account.save()

        refreshed_account = BankAccount.objects.get(id=self.bank_account.id)
        self.assertEqual(refreshed_account.bank_name, test_bank_name)
        self.assertEqual(refreshed_account.account_name, test_account_name)
    
    # test multiple accounts
    def test_multiple_accounts_per_user(self):
        account2 = BankAccountFactory(user=self.user)
        account3 = BankAccountFactory(user=self.user)
        user_accounts = BankAccount.objects.filter(user=self.user)
        self.assertEqual(user_accounts.count(), 3)
        self.assertIn(self.bank_account, user_accounts)
        self.assertIn(account2, user_accounts)
        self.assertIn(account3, user_accounts)