from django.urls import path
from alerts.views import *

# Setting the allowed urls for the app
urlpatterns = [
    path('messages/', messages_view , name='messages'),
    path('get-messages/', get_messages, name='get_messages'),
    path('delete-message/<int:message_id>/', delete_message, name='delete_message'),
    path('count-unread-messages/', count_unread_messages, name='count_unread_messages'),
]