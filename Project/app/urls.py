from django.urls import path
from app.views import *

# Setting the allowed urls for the app
urlpatterns = [
    path('savings/', savings_view, name='savings'),
    path('add-savings-goal/', add_goal, name='add_savings_goal'),
    path('get-all-goals/', get_all_goals, name='get_all_goals'),
    path('edit-goal/<int:goal_id>/', edit_goal, name='edit_goal'),
    path('delete-goal/<int:goal_id>/', delete_goal, name='delete_goal'),
    path('budgets/', budgets_view, name='budgets'),
    path('get-all-budgets/', get_all_budgets, name='get_all_budgets'),
    path('add-budget/', add_budget, name='add_budget'),
    path('edit-budget/<int:budget_id>/', edit_budget, name='edit_budget'),
    path('delete-budget/<int:budget_id>/', delete_budget, name='delete_budget'),
    path('update-budget-progress/<int:budget_id>/', update_budget_progress, name='update_budget_progress'),
    path('get-all-transactions-insights/', get_all_transactions_insights, name='get_all_transactions_insights'),
    path('get-category-breakdown/', get_category_breakdown, name='get_category_breakdown'),
    path('get-account-breakdown/', get_account_breakdown, name='get_account_breakdown'),
    path('get-spending-statistics/', get_spending_statistics, name='get_spending_statistics'),
    path('insights/', insights_view, name='insights'),
    path('messages/', messages_view , name='messages'),
    path('get-messages/', get_messages, name='get_messages'),
    path('delete-message/<int:message_id>/', delete_message, name='delete_message'),
    path('count-unread-messages/', count_unread_messages, name='count_unread_messages'),
]