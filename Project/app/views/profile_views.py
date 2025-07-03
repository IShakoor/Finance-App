from django.contrib.auth import update_session_auth_hash
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from accounts.models import CustomUser
import json
import re

@login_required
def profile_view(request):
    return render(request, 'app/profile.html')

# edit user details
@csrf_protect
@require_POST
@login_required
def edit_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    if user != request.user:
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    # fetch details
    try:
        data = json.loads(request.body)
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        current_password = data.get('current_password')
        password_confirm = data.get('password_confirm')

        # validation
        if not username or not email or not current_password:
            return JsonResponse({'error': 'Username, email, and current password are required.'}, status=400)
        if not user.check_password(current_password):
            return JsonResponse({'error': 'Incorrect current password.'}, status=400)
        
        # check for duplicate username
        duplicate_username = False
        for existing_user in CustomUser.objects.exclude(id=user.id):
            if existing_user.username.lower() == username.lower():
                duplicate_username = True
                break
        
        if duplicate_username:
            return JsonResponse({'error': 'Username already exists.'}, status=400)
        
        # check for duplicate email
        duplicate_email = False
        for existing_user in CustomUser.objects.exclude(id=user.id):
            if existing_user.email.lower() == email.lower():
                duplicate_email = True
                break
        
        if duplicate_email:
            return JsonResponse({'error': 'Email already exists.'}, status=400)

        # validation - new passwords
        if password:
            if password != password_confirm:
                return JsonResponse({'error': 'Passwords do not match.'}, status=400)
            if len(password) < 8:
                return JsonResponse({'error': 'Password must be at least 8 characters long.'}, status=400)
            if not re.search(r"[A-Z]", password):
                return JsonResponse({'error': 'Password must contain at least one uppercase letter.'}, status=400)
            if not re.search(r"\d", password):
                return JsonResponse({'error': 'Password must contain at least one number.'}, status=400)
            if not re.search(r"[!@#$%^&*.]", password):
                return JsonResponse({'error': 'Password must contain at least one special character (!@#$%^&*.).'}, status=400)
            if username and password.lower() == username.lower():
                return JsonResponse({'error': 'Password cannot be the same as your username.'}, status=400)
            if email and password.lower() == email.lower():
                return JsonResponse({'error': 'Password cannot be the same as your email.'}, status=400)

        # update details
        if username:
            user.username = username
        if email:
            user.email = email
        if password:
            user.set_password(password)
            update_session_auth_hash(request, user)
        user.save()
        return JsonResponse({'success': True})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# delete user account
@csrf_protect
@require_POST
@login_required
def delete_account(request):
    try:
        user = request.user
        user.delete()
        logout(request)
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)