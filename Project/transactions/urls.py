from django.urls import path
from transactions.views import *

# transaction urls
urlpatterns = [
    path('get-all-transactions/', get_all_transactions, name='get_all_transactions'),
    path('get-categories/', get_categories, name='get_categories'),
    path('get-bank-accounts/', get_bank_accounts, name='get_bank_accounts'),
    path('transactions/', transactions_page, name='transactions'),
    path('add-transaction/', add_transaction, name='add_transaction'),
    path('edit-transaction/<int:transaction_id>/', edit_transaction, name='edit_transaction'),
    path('delete-transaction/<int:transaction_id>/', delete_transaction, name='delete_transaction'),
]