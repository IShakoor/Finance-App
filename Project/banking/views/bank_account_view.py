from django.http import JsonResponse
from banking.views.plaid_client import get_plaid_client
from banking.models import BankAccount
from plaid.model.accounts_get_request import AccountsGetRequest
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import csrf_protect

# sync bank account data from api
@login_required
@require_POST
def sync_bank_accounts(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "User is not authenticated."}, status=401)

    # connect to api
    try:
        client = get_plaid_client()
        access_token = request.user.plaid_access_token
        if not access_token:
            return JsonResponse({"error": "Access token not found for user."}, status=400)

        # fetch accounts from api
        request_data = AccountsGetRequest(access_token=access_token)
        response = client.accounts_get(request_data)
        plaid_accounts = response.to_dict().get("accounts", [])

        existing_accounts = set(BankAccount.objects.filter(user=request.user).values_list('account_id', flat=True))
        new_accounts = []

        account_type_mapping = {
            "depository": {"checking": "Checking", "savings": "Savings"},
            "credit": "Credit Card",
            "loan": "Loan",
            "investment": "Investment",
            "other": "Other",
        }

        # collect account data
        for account in plaid_accounts:
            account_id = account["account_id"]
            if account_id not in existing_accounts:
                plaid_type = account["type"]
                plaid_subtype = account.get("subtype", "")

                account_type = account_type_mapping.get(plaid_type, "Other")
                if isinstance(account_type, dict):
                    account_type = account_type.get(plaid_subtype, "Other")

                # create account model
                new_accounts.append(
                    BankAccount(
                        user=request.user,
                        bank_name=account.get("official_name", "Unknown Bank"),
                        account_name=account.get("name", ""),
                        account_id=account_id,
                        account_type=account_type,
                        balance=str(account["balances"]["current"]),
                        currency=account["balances"].get("iso_currency_code", "GBP"),
                        last_synced=datetime.utcnow(),
                        is_active=True
                    )
                )

        # save to database
        BankAccount.objects.bulk_create(new_accounts)

        return JsonResponse({"success": f"{len(new_accounts)} accounts synced."})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
# get account balance from database
@login_required
@require_GET
def get_account_balance(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "User is not authenticated."}, status=401)

    # fetch bank account data
    try:
        accounts = BankAccount.objects.filter(user=request.user)
        if not accounts.exists():
            return JsonResponse({"message": "No accounts detected."})
        
        accounts_list = [
            {
                "id": acc.id,
                "bank_name": acc.bank_name,
                "account_name": acc.account_name,
                "account_type": acc.account_type,
                "balance": acc.decrypted_balance,
                "currency": acc.currency,
                "last_synced": acc.last_synced.isoformat(),
                "is_active": acc.is_active,
            }
            for acc in accounts
        ]

        return JsonResponse({"accounts": accounts_list})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
# delete bank accounts
@csrf_protect
@require_POST
@login_required
def delete_bank_account(request, account_id):
    try:
        account = BankAccount.objects.get(id=account_id, user=request.user)
        account.delete()
        return JsonResponse({'success': True})
    except BankAccount.DoesNotExist:
        return JsonResponse({'error': 'Bank account not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)