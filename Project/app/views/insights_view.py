from banking.views.plaid_client import *
from transactions.models import Transaction
from datetime import datetime
from transactions.views.transactions_view import sync_transactions
from django.http import JsonResponse
from django.shortcuts import render
from collections import defaultdict
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET

# render template
@login_required
def insights_view(request):
    return render(request, 'app/insights.html', {
        'user': request.user
    })

# fetch all transactions
def fetch_transactions(user):
    sync_transactions(user)

    # fetch transactions the database
    transactions = Transaction.objects.filter(user=user, bank_account__isnull=False).values(
        'id', 'name', 'amount', 'date', 'category', 'is_received', 'bank_account_id', 'bank_account__account_name'
    )

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
            'account_name': txn['bank_account__account_name']
        }
        for txn in transactions
    ]

    return formatted_transactions

# get all transactions for insights
@login_required
@require_GET
def get_all_transactions_insights(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "User is not authenticated."}, status=401)

    try:
        transactions = fetch_transactions(request.user)

        if not transactions:
            return JsonResponse({"transactions": []})

        # sort transactions in descending order
        sorted_transactions = sorted(
            transactions,
            key=lambda x: datetime.strptime(x['date'], '%Y-%m-%d'),
            reverse=True
        )

        return JsonResponse({
            'transactions': sorted_transactions,
        })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

# get category breakdown data
@login_required
@require_GET
def get_category_breakdown(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'User is not authenticated.'}, status=401)

    try:
        # fetch all transactions
        transactions = fetch_transactions(request.user)

        # filter for spent transactions
        spent_transactions = [txn for txn in transactions if not txn['is_received']]

        # calculate spending per category & collect dates
        total_spent = 0
        category_spending = defaultdict(float)

        for transaction in spent_transactions:
            amount = transaction['amount']
            total_spent += amount
            category_spending[transaction['category']] += amount

        # split data into lists for charts
        categories = list(category_spending.keys())
        amounts = [category_spending[cat] for cat in categories]
        percentages = [round((amount / total_spent) * 100) for amount in amounts]

        return JsonResponse({
            'categories': categories,
            'amounts': amounts,
            'percentages': percentages,
            'total_spent': total_spent,
        })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
# get account breakdown
@login_required
@require_GET
def get_account_breakdown(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'User is not authenticated.'}, status=401)

    try:
        # fetch all transactions
        transactions = fetch_transactions(request.user)

        # calculate transaction count per account
        account_transaction_count = defaultdict(int)

        for transaction in transactions:
            account_transaction_count[transaction['account_name']] += 1

        # calculate total number of transactions
        total_transactions = len(transactions)

        # split data into lists for charts
        accounts = list(account_transaction_count.keys())
        transaction_counts = [account_transaction_count[account] for account in accounts]
        percentages = [round((count / total_transactions) * 100) for count in transaction_counts]

        return JsonResponse({
            'accounts': accounts,
            'transaction_counts': transaction_counts,
            'percentages': percentages,
            'total_transactions': total_transactions,
        })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
# get spending stats
@login_required
@require_GET
def get_spending_statistics(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'User is not authenticated.'}, status=401)

    try:
        # fetch all transactions
        transactions = fetch_transactions(request.user)

        if not transactions:
            return JsonResponse({
                "highest_received_transaction": None,
                "highest_spent_transaction": None,
                "transaction_count": 0
            })

        # separate received & sent transactions
        received_transactions = [txn for txn in transactions if txn['is_received']]
        spent_transactions = [txn for txn in transactions if not txn['is_received']]

        # get highest received and sent
        highest_received_transaction = max(received_transactions, key=lambda txn: txn['amount'], default=None)
        highest_spent_transaction = max(spent_transactions, key=lambda txn: txn['amount'], default=None)

        transaction_count = len(transactions)

        return JsonResponse({
            'highest_received_transaction': highest_received_transaction,
            'highest_spent_transaction': highest_spent_transaction,
            'transaction_count': transaction_count
        })
    
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
