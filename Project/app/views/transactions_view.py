from django.core.paginator import Paginator
from app.views.plaid_client import *
from app.models import Transaction
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST, require_GET
from django.contrib.auth.decorators import login_required
from datetime import datetime
from plaid.model.transactions_sync_request import TransactionsSyncRequest
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from app.models.bankAccount import BankAccount

# render transaction page
@login_required
def transactions_page(request):
    return render(request, 'app/transactions.html')

# get all transactions
@require_GET
@login_required
def get_all_transactions(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "User is not authenticated."}, status=401)

    try:
        # sync transactions with api
        sync_transactions(request.user)

        # prevent duplicate transactions
        transactions_query = Transaction.objects.filter(user=request.user, bank_account__isnull=False).distinct()

        # fetch transactions from database
        transactions = transactions_query.values(
            'id', 'name', 'amount', 'date', 'category', 'is_received', 'bank_account_id','bank_account__account_name', 'transaction_id'
        )

        if not transactions:
            return JsonResponse({"transactions": [], "page": 1, "total_pages": 1})

        # format transactions
        formatted_transactions = [
            {
                'id': txn['id'],
                'name': txn['name'].strip(),
                'amount': abs(float(txn['amount'])),
                'date': txn['date'].strftime('%Y-%m-%d'),
                'category': txn['category'] or 'Uncategorized',
                'is_received': txn['is_received'],
                'bank_account_id': txn['bank_account_id'],
                'account_name': txn['bank_account__account_name'],
                'transaction_id': txn['transaction_id']
            }
            for txn in transactions
        ]

        # searching and filtering
        filters = {
            'search': lambda txn: request.GET.get('search', '').lower() in txn['name'].lower(),
            'category': lambda txn: txn['category'].lower() == request.GET.get('category', '').lower(),
            'start_date': lambda txn: txn['date'] >= request.GET.get('start_date', ''),
            'end_date': lambda txn: txn['date'] <= request.GET.get('end_date', ''),
            'min_price': lambda txn: txn['amount'] >= float(request.GET.get('min_price', 0)),
            'max_price': lambda txn: txn['amount'] <= float(request.GET.get('max_price', float('inf'))),
            'type': lambda txn: txn['is_received'] == (request.GET.get('type', '').lower() == 'received'),
            'bank_account': lambda txn: txn['bank_account_id'] == int(request.GET.get('bank_account')) if request.GET.get('bank_account') else True,
        }

        for key, condition in filters.items():
            if request.GET.get(key):
                formatted_transactions = [txn for txn in formatted_transactions if condition(txn)]

        # sort transactions in descending order
        sorted_transactions = sorted(
            formatted_transactions,
            key=lambda x: datetime.strptime(x['date'], '%Y-%m-%d'),
            reverse=True
        )

        # paginate results (50 transactions per page)
        paginator = Paginator(sorted_transactions, 50)
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)

        return JsonResponse({
            'transactions': list(page_obj),
            'page': page_obj.number,
            'total_pages': paginator.num_pages,
        })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

# fetch categories for filtering
@login_required
@require_GET
def get_categories(request):
    # check authentication
    if not request.user.is_authenticated:
        return JsonResponse({"error": "User is not authenticated."}, status=401)

    try:
        # get API transactions
        client = get_plaid_client()
        access_token = request.user.plaid_access_token
        if not access_token:
            return JsonResponse({"error": "Access token not found for user."}, status=400)

        cursor = None
        plaid_categories = set() # set to avoid duplications

        while True:
            request_data = TransactionsSyncRequest(
                access_token=access_token, cursor=cursor
            ) if cursor else TransactionsSyncRequest(access_token=access_token)
            response = client.transactions_sync(request_data)

            # find categories from transactions
            for txn in response.added:
                if txn.personal_finance_category and txn.personal_finance_category.primary:
                    plaid_categories.add(txn.personal_finance_category.primary.replace('_', ' '))
                else:
                    plaid_categories.add('Uncategorized')

            cursor = response.next_cursor
            if not response.has_more:
                break

        # fetch categories from custom transactions in database
        db_categories = Transaction.objects.filter(user=request.user).values_list('category', flat=True)
        db_categories = set(filter(None, db_categories))

        # combine & sort categories
        all_categories = sorted(plaid_categories.union(db_categories))
        return JsonResponse(list(all_categories), safe=False)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
# get accounts for filters
@login_required
@require_GET
def get_bank_accounts(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "User is not authenticated."}, status=401)

    try:
        accounts = BankAccount.objects.filter(user=request.user, is_active=True)
        account_data = [{
            'id': account.id,
            'bank_name': account.bank_name,
            'account_name': account.account_name,
            'account_type': account.account_type
        } for account in accounts]
        return JsonResponse(account_data, safe=False)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

# add a new transaction
@csrf_protect
@require_POST
@login_required
def add_transaction(request):
    try:
        data = json.loads(request.body)

        # set fields
        name = data.get('name')
        amount = float(data.get('amount'))
        date = datetime.strptime(data.get('date'), '%Y-%m-%d')
        category = data.get('category', 'Custom')
        is_received = data.get('is_received', False)
        bank_account_id = data.get('bank_account')
        transaction_id = data.get('transaction_id')
        
        bank_account = get_object_or_404(BankAccount, id=bank_account_id, user=request.user)

        if not name or amount is None or not date:
            return JsonResponse({'error': 'Invalid input data.'}, status=400)

        # adjust amount based on is_received
        if not is_received:
            amount = -abs(amount) 
        else:
            amount = abs(amount)

        # save transaction
        transaction = Transaction.objects.create(
            user=request.user,
            bank_account=bank_account,
            name=name,
            amount=str(amount),
            date=date,
            category=category,
            is_received=is_received,
            transaction_id=transaction_id
        )

        # return success response
        return JsonResponse({
            'success': True,
            'transaction': {
                'name': transaction.name,
                'amount': float(transaction.amount),
                'date': transaction.date.strftime('%Y-%m-%d'),
                'category': transaction.category,
                'is_received': transaction.is_received,
                'transaction_id': transaction.transaction_id
            }
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# sync transactions with database
def sync_transactions(user):
    try:
        # connect to the API
        client = get_plaid_client()
        access_token = user.plaid_access_token
        if not access_token:
            return {"error": "Access token not found for user."}

        cursor = None
        new_transactions = []
        processed_count = 0
        skipped_count = 0

        # get all bank accounts for the user
        bank_accounts = BankAccount.objects.filter(user=user)

        # use a set to track transaction IDs
        existing_transaction_ids = set(
            Transaction.objects.filter(user=user).values_list('transaction_id', flat=True)
        )

        # collect transactions from api
        while True:
            request_data = TransactionsSyncRequest(
                access_token=access_token, cursor=cursor
            ) if cursor else TransactionsSyncRequest(access_token=access_token)

            response = client.transactions_sync(request_data)
            plaid_transactions = response.added

            # use transaction id to prvent duplication
            for txn in plaid_transactions:
                if txn.transaction_id in existing_transaction_ids:
                    skipped_count += 1
                    continue

                # find matching bank account
                matching_account = next((account for account in bank_accounts if account.account_id == txn.account_id), None)

                if not matching_account:
                    skipped_count += 1
                    continue

                # determine category using personal_finance_category.primary if available
                if txn.personal_finance_category and txn.personal_finance_category.primary:
                    category = txn.personal_finance_category.primary.replace('_', ' ')
                else:
                    category = 'Uncategorized'
                
                # create transaction
                try:
                    new_transaction = Transaction(
                        user=user,
                        bank_account=matching_account,
                        name=txn.name.strip(),
                        amount=str(txn.amount),
                        date=txn.date,
                        category=category,
                        is_received=txn.amount < 0,
                        transaction_id=txn.transaction_id
                    )
                    
                    # create transaction and log id
                    new_transactions.append(new_transaction)
                    existing_transaction_ids.add(txn.transaction_id)
                    processed_count += 1
                except Exception as e:
                    continue

            if not response.has_more:
                break
            cursor = response.next_cursor

        # bulk create new transactions
        if new_transactions:
            Transaction.objects.bulk_create(new_transactions)

    except Exception as e:
        error_message = f"Error in sync_transactions: {str(e)}"
        return {"error": error_message}
    
# delete transaction
@csrf_protect
@require_POST
@login_required
def delete_transaction(request, transaction_id):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'User is not authenticated.'}, status=401)

    try:
        get_object_or_404(Transaction, id=transaction_id, user=request.user).delete()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# edit transactions
@csrf_protect
@require_POST
@login_required
def edit_transaction(request, transaction_id):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'User is not authenticated.'}, status=401)

    transaction = get_object_or_404(Transaction, id=transaction_id, user=request.user)
    try:
        data = json.loads(request.body)
        
        # updated fields
        for field in ['name', 'amount', 'date', 'is_received', 'category']:
            if field in data:
                if field == 'amount':
                    setattr(transaction, field, str(float(data[field])))
                elif field == 'date':
                    setattr(transaction, field, datetime.strptime(data[field], '%Y-%m-%d'))
                else:
                    setattr(transaction, field, data[field])

        transaction.save()

        return JsonResponse({
            "success": True,
            "message": "Transaction updated successfully",
            "transaction": {
                "id": transaction.id,
                "name": transaction.name,
                "amount": float(transaction.amount),
                "date": transaction.date.strftime('%Y-%m-%d'),
                "category": transaction.category,
                "is_received": transaction.is_received,
                "transaction_id": transaction.transaction_id,
                "account_name": transaction.bank_account.account_name
            }
        })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
# UPDATE TRANSACTION CATEGORIES:
# REPLACE '_' IN CATS WITH SPACE
# CHECK BUDGET/SAVINGS CATEGORIES ALSO