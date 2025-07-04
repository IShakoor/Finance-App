from django.urls import path
from analytics.views import *

# insights URLS
urlpatterns = [
    path('get-all-transactions-insights/', get_all_transactions_insights, name='get_all_transactions_insights'),
    path('get-category-breakdown/', get_category_breakdown, name='get_category_breakdown'),
    path('get-account-breakdown/', get_account_breakdown, name='get_account_breakdown'),
    path('get-spending-statistics/', get_spending_statistics, name='get_spending_statistics'),
    path('insights/', insights_view, name='insights'),
]