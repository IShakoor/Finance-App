from django.urls import path
from savings.views import *

# Setting the allowed urls for the app
urlpatterns = [
    path('savings/', savings_view, name='savings'),
    path('add-savings-goal/', add_goal, name='add_savings_goal'),
    path('get-all-goals/', get_all_goals, name='get_all_goals'),
    path('edit-goal/<int:goal_id>/', edit_goal, name='edit_goal'),
    path('delete-goal/<int:goal_id>/', delete_goal, name='delete_goal'),
]