from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_GET
import json
from alerts.models import Message
from budgets.models import Budget
from transactions.models import Transaction
from django.utils import timezone
from decimal import Decimal

# render the budget page
@login_required
def budgets_view(request):
    return render(request, "budgets/budgets.html")

# get all budgets
@login_required
@require_GET
def get_all_budgets(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "User is not authenticated."}, status=401)

    budgets = Budget.objects.filter(user=request.user).order_by('created_date')

    formatted_budgets = []
    for budget in budgets:
        formatted_budgets.append({
            "id": budget.id,
            "name": budget.name,
            "target_amount": float(budget.target_amount),
            "current_amount": abs(float(budget.current_amount)),
            "time_period": budget.time_period,
            "category": budget.category,
            "created_date": budget.created_date.strftime('%Y-%m-%d %H:%M:%S'),
            "last_reset_date": budget.last_reset_date.strftime('%Y-%m-%d')
        })

    return JsonResponse({"budgets": formatted_budgets})

# add new budget
@csrf_protect
@login_required
@require_POST
def add_budget(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'User is not authenticated.'}, status=401)
    
    try:
        data = json.loads(request.body)
        budget = Budget.objects.create(
            user=request.user,
            name=data['name'],
            target_amount=float(data['target_amount']),
            time_period=data['time_period'],
            category=data['category']
        )

        return JsonResponse({'success': True, 'budget': {
            'id': budget.id, 'name': budget.name,
            'target_amount': float(budget.target_amount),
            'current_amount': float(budget.current_amount),
            'time_period': budget.time_period,
            'category': budget.category
        }})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# delete budget
@csrf_protect
@require_POST
@login_required
def delete_budget(request, budget_id):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'User is not authenticated.'}, status=401)

    try:
        get_object_or_404(Budget, id=budget_id, user=request.user).delete()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# edit budget
@csrf_protect
@require_POST
@login_required
def edit_budget(request, budget_id):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'User is not authenticated.'}, status=401)

    budget = get_object_or_404(Budget, id=budget_id, user=request.user)
    try:
        data = json.loads(request.body)
        for field in ['name', 'target_amount', 'time_period', 'category']:
            setattr(budget, field, float(data[field]) if 'amount' in field else data[field])
        budget.save()
        return JsonResponse({"message": "Budget updated successfully", "current_amount": float(budget.current_amount)})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_protect
@require_POST
@login_required
def update_budget_progress(request, budget_id):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'User is not authenticated.'}, status=401)
    try:
        budget = get_object_or_404(Budget, id=budget_id, user=request.user)

        today = timezone.now().date()

        # check if budget reset is needed
        should_reset = False
        if budget.time_period == 'weekly':
            days_since_reset = (today - budget.last_reset_date).days
            should_reset = days_since_reset >= 7
        elif budget.time_period == 'monthly':
            should_reset = today.month != budget.last_reset_date.month or today.year != budget.last_reset_date.year
        elif budget.time_period == 'annually':
            should_reset = today.year != budget.last_reset_date.year

        # reset budget variables if needed
        if should_reset:
            budget.current_amount = Decimal('0')
            budget.last_reset_date = today
            budget.save()

        transactions = Transaction.objects.filter(user=request.user)

        filtered_transactions = [
            x for x in transactions
            if x.category == budget.category and not x.is_received and x.date >= budget.last_reset_date
        ]
        
        # calculate total spent
        total_spent = sum(abs(Decimal(t.amount)) for t in filtered_transactions)

        # update budget values if needed
        if budget.current_amount != min(total_spent, budget.target_amount):
            budget.current_amount = min(total_spent, budget.target_amount)
            budget.save()

        # check if budget is above 75%
        threshold = Decimal('0.75')
        is_approaching_limit = budget.current_amount >= budget.target_amount * threshold

        if is_approaching_limit:
            try:
                Message.objects.create(
                    user=request.user,
                    title=f"Budget Alert: {budget.name}",
                    content=f"Your budget '{budget.name}' is {int((budget.current_amount / budget.target_amount) * 100)}% complete.",
                )
            except Exception as e:
                return JsonResponse({"error": str(e)}, status=500)

        return JsonResponse({
            'success': True, 
            'current_amount': float(budget.current_amount),
            'total_transactions': len(filtered_transactions),
            'total_spent': total_spent,
            'is_approaching_limit': is_approaching_limit,
        })

    except Exception as e:
        return JsonResponse({
            'success': False, 
            'error': str(e)
        }, status=500)