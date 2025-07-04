from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST, require_GET
from django.contrib.auth.decorators import login_required
from datetime import datetime
import json
from alerts.models import Message
from savings.models import SavingsGoal
from decimal import Decimal

# render html page
@login_required
def savings_view(request):
    return render(request, "savings/savings.html")

# load goals
@require_GET
@login_required
def get_all_goals(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "User is not authenticated."}, status=401)

    goals = SavingsGoal.objects.filter(user=request.user).order_by('goal_date').values(
        'id', 'name', 'target_amount', 'current_amount', 'goal_date', 'created_date'
    )

    formatted_goals = [
        {**goal, 'target_amount': float(goal['target_amount']),
         'current_amount': float(goal['current_amount']),
         'goal_date': goal['goal_date'].strftime('%Y-%m-%d'),
         'created_date': goal['created_date'].strftime('%Y-%m-%d %H:%M:%S')}
        for goal in goals
    ]

    return JsonResponse({'goals': formatted_goals})

# add new goal
@csrf_protect
@login_required
@require_POST
def add_goal(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'User is not authenticated.'}, status=401)
    
    try:
        data = json.loads(request.body)
        goal = SavingsGoal.objects.create(
            user=request.user,
            name=data['name'],
            target_amount=float(data['target_amount']),
            current_amount=float(data.get('current_amount', 0.00)),
            goal_date=datetime.strptime(data['goal_date'], '%Y-%m-%d')
        )
        
        return JsonResponse({'success': True, 'goal': {
            'id': goal.id, 'name': goal.name,
            'target_amount': float(goal.target_amount),
            'current_amount': float(goal.current_amount),
            'goal_date': goal.goal_date.strftime('%Y-%m-%d')
        }})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# delete goal
@csrf_protect
@require_POST
@login_required
def delete_goal(request, goal_id):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'User is not authenticated.'}, status=401)

    try:
        get_object_or_404(SavingsGoal, id=goal_id, user=request.user).delete()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# edit goal
@csrf_protect
@require_POST
@login_required
def edit_goal(request, goal_id):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'User is not authenticated.'}, status=401)

    goal = get_object_or_404(SavingsGoal, id=goal_id, user=request.user)
    try:
        data = json.loads(request.body)

        # robust data handling with Decimal
        goal.name = data['name']
        goal.target_amount = Decimal(data['target_amount'])
        goal.current_amount = Decimal(data['current_amount'])

        # more robust date handling with error checking
        try:
            goal.goal_date = datetime.strptime(data['goal_date'], '%Y-%m-%d').date()
        except ValueError as e:
            return JsonResponse({'error': f"Invalid date format: {e}"}, status=400)

        goal.save()

        # create message if over 75% complete
        threshold = Decimal('0.75')
        is_approaching_limit = goal.current_amount >= goal.target_amount * threshold

        if is_approaching_limit:
            try:
                percentage_complete = int((goal.current_amount / goal.target_amount) * 100)
                Message.objects.create(
                    user=request.user,
                    title=f"Goal Alert: {goal.name}",
                    content=f"Your savings goal '{goal.name}' is {percentage_complete}% complete.",
                )
            except Exception as e:
                return JsonResponse({'error': f"Failed to create message: {e}"}, status=500)

        return JsonResponse({"message": "Goal updated successfully"})
    except (KeyError, ValueError, TypeError) as e:
        return JsonResponse({"error": f"Invalid data: {e}"}, status=400)
    except Exception as e:
        return JsonResponse({"error": f"Server error: {e}"}, status=500)
