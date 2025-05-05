from django.test import TestCase
from django.core.exceptions import ValidationError
from app.models import Transaction
from app.tests.factories import UserFactory, BankAccountFactory, TransactionFactory
import uuid

# transaction models test
class TransactionModelTests(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.bank_account = BankAccountFactory(user=self.user)
    
    # test valid transaction creation
    def test_create_transaction(self):
        transaction = TransactionFactory(
            user=self.user,
            bank_account=self.bank_account,
            amount="100.50",
            name="Test Transaction",
            is_received=True
        )
        self.assertEqual(transaction.user, self.user)
        self.assertEqual(transaction.bank_account, self.bank_account)
        self.assertEqual(transaction.amount, "100.50")
        self.assertEqual(transaction.name, "Test Transaction")
        self.assertTrue(transaction.is_received)
        self.assertIsNotNone(transaction.transaction_id)
    
    # test amount decrypting
    def test_decrypted_amount_property(self):
        transaction = TransactionFactory(
            user=self.user,
            bank_account=self.bank_account,
            amount="123.45"
        )
        self.assertEqual(transaction.decrypted_amount, 123.45)
        transaction.decrypted_amount = 250.75
        self.assertEqual(transaction.amount, "250.75")
        self.assertEqual(transaction.decrypted_amount, 250.75)
    
    # test tostring function
    def test_string_representation(self):
        transaction = Transaction.objects.create(
            user=self.user,
            bank_account=self.bank_account,
            name="Test Transaction",
            amount="75.25",
            date="2023-01-15",
            transaction_id=str(uuid.uuid4())
        )
        expected_str = f"Test Transaction - £75.25 - 2023-01-15"
        self.assertEqual(str(transaction), expected_str)
    
    # test megative amounts
    def test_negative_amount_validation(self):
        transaction = Transaction(
            user=self.user,
            bank_account=self.bank_account,
            name="Negative Transaction",
            amount="-50.00",
            date="2023-01-15",
            transaction_id=str(uuid.uuid4())
        )
        with self.assertRaises(ValidationError) as context:
            transaction.clean()
        self.assertIn('amount', context.exception.error_dict)
        self.assertEqual(
            context.exception.error_dict['amount'][0].message,
            'Amount must be a positive value.'
        )
    
    # test zero amounts
    def test_zero_amount_validation(self):
        transaction = Transaction(
            user=self.user,
            bank_account=self.bank_account,
            name="Zero Transaction",
            amount="0.00",
            date="2023-01-15",
            transaction_id=str(uuid.uuid4())
        )
        with self.assertRaises(ValidationError) as context:
            transaction.clean()
        self.assertIn('amount', context.exception.error_dict)
        self.assertEqual(
            context.exception.error_dict['amount'][0].message,
            'Amount must be a positive value.'
        )

    # test invalud amounts
    def test_invalid_amount_validation(self):
        transaction = Transaction(
            user=self.user,
            bank_account=self.bank_account,
            name="Invalid Transaction",
            amount="not-a-number",
            date="2023-01-15",
            transaction_id=str(uuid.uuid4())
        )
        with self.assertRaises(ValidationError) as context:
            transaction.clean()
        self.assertIn('amount', context.exception.error_dict)
        self.assertEqual(
            context.exception.error_dict['amount'][0].message,
            'Invalid amount value.'
        )

    # test unique ids
    def test_transaction_id_uniqueness(self):
        transaction_id = str(uuid.uuid4())
        transaction1 = Transaction.objects.create(
            user=self.user,
            bank_account=self.bank_account,
            name="First Transaction",
            amount="100.00",
            date="2023-01-15",
            transaction_id=transaction_id
        )
        with self.assertRaises(Exception):
            transaction2 = Transaction.objects.create(
                user=self.user,
                bank_account=self.bank_account,
                name="Second Transaction",
                amount="200.00",
                date="2023-01-16",
                transaction_id=transaction_id
            )
    
    # testing cascades
    def test_delete_user_cascades_to_transaction(self):
        transaction = TransactionFactory(user=self.user, bank_account=self.bank_account)
        transaction_id = transaction.id
        self.assertTrue(Transaction.objects.filter(id=transaction_id).exists())
        self.user.delete()
        self.assertFalse(Transaction.objects.filter(id=transaction_id).exists())
    
    # testing delete bank account cascades to transactions
    def test_delete_bank_account_cascades_to_transaction(self):
        transaction = TransactionFactory(user=self.user, bank_account=self.bank_account)
        transaction_id = transaction.id
        self.assertTrue(Transaction.objects.filter(id=transaction_id).exists())
        self.bank_account.delete()
        self.assertFalse(Transaction.objects.filter(id=transaction_id).exists())
    
    # test category can be null
    def test_category_can_be_null(self):
        transaction = Transaction.objects.create(
            user=self.user,
            bank_account=self.bank_account,
            name="No Category Transaction",
            amount="100.00",
            date="2023-01-15",
            category=None,
            transaction_id=str(uuid.uuid4())
        )
        self.assertIsNone(transaction.category)
        
    # test is_received defaults to false
    def test_is_received_default_value(self):
        transaction = Transaction.objects.create(
            user=self.user,
            bank_account=self.bank_account,
            name="Default Transaction",
            amount="100.00",
            date="2023-01-15",
            transaction_id=str(uuid.uuid4())
        )
        self.assertFalse(transaction.is_received)
    
    # add multiple transactions at once
    def test_bulk_create_transactions(self):
        transactions_data = [
            {
                "name": "Transaction 1",
                "amount": "100.00",
                "date": "2023-01-15",
                "transaction_id": str(uuid.uuid4())
            },
            {
                "name": "Transaction 2",
                "amount": "200.00",
                "date": "2023-01-16",
                "transaction_id": str(uuid.uuid4())
            },
            {
                "name": "Transaction 3",
                "amount": "300.00",
                "date": "2023-01-17",
                "transaction_id": str(uuid.uuid4())
            }
        ]
        
        transaction_ids = []
        transactions = []
        for data in transactions_data:
            transaction_ids.append(data["transaction_id"])
            transactions.append(Transaction(
                user=self.user,
                bank_account=self.bank_account,
                **data
            ))

        Transaction.objects.bulk_create(transactions)
        
        self.assertEqual(Transaction.objects.filter(user=self.user).count(), 3)
        transaction = Transaction.objects.get(transaction_id=transaction_ids[1])
        self.assertEqual(transaction.name, "Transaction 2")
        self.assertEqual(transaction.amount, "200.00")
        self.assertEqual(transaction.date.isoformat(), "2023-01-16")