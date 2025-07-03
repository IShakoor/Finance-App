from django.urls import path
from accounts.views import *

# account management URLS
urlpatterns = [
    path('signup/', signup_view, name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('password-reset/', password_reset_request, name='password_reset'),
    path('password-reset/<int:user_id>/', password_reset_confirm_view, name='password_reset_confirm'),
    path('verify-2fa/', verify_2fa_view, name='verify_2fa'),
    path('profile/', profile_view, name='profile'),
    path('edit-user/<int:user_id>/', edit_user, name='edit_user'),
    path('delete-account/', delete_account, name='delete_account'),
]