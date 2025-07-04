from django.urls import path
from budgets.views import *

# setting budget URLS
urlpatterns = [
    path('budgets/', budgets_view, name='budgets'),
    path('get-all-budgets/', get_all_budgets, name='get_all_budgets'),
    path('add-budget/', add_budget, name='add_budget'),
    path('edit-budget/<int:budget_id>/', edit_budget, name='edit_budget'),
    path('delete-budget/<int:budget_id>/', delete_budget, name='delete_budget'),
    path('update-budget-progress/<int:budget_id>/', update_budget_progress, name='update_budget_progress'),
]