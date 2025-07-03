from django.urls import path
from banking.views import *

# banking URLS
urlpatterns = [
    path('exchange-public-token/', exchange_public_token, name='exchange_public_token'),
    path('create-link-token/', create_link_token, name='create_link_token'),
    path('sync-bank-accounts/', sync_bank_accounts, name='sync_bank_accounts'),
    path('get-account-balance/', get_account_balance, name='get_account_balance'),
    path('delete-bank-account/<int:account_id>/', delete_bank_account, name='delete_bank_account'),
]