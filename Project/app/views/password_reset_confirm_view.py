from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import get_user_model
from app.forms.password_reset_confirm_form import PasswordResetConfirmForm
from django.views.decorators.http import require_http_methods

User = get_user_model()

@require_http_methods(['GET', 'POST'])
def password_reset_confirm(request, user_id):
    try:
        user = get_object_or_404(User, id=user_id)
    except User.DoesNotExist:
        messages.error(request, "Invalid user.")
        return redirect('password_reset')

    if request.method == 'POST':
        form = PasswordResetConfirmForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data['password1']
            user.set_password(password)
            user.save()
            messages.success(request, "Your password has been reset successfully.")
            return redirect('login')
    else:
        form = PasswordResetConfirmForm()

    return render(request, 'app/password_reset_confirm.html', {'form': form})