from django.shortcuts import render, redirect
from django.core.mail import send_mail
from accounts.models.user import CustomUser
from django.contrib import messages
from accounts.forms.password_reset_request_form import PasswordResetForm
from django.urls import reverse
from django.conf import settings

# allow user to enter email - then send recover link to email
def password_reset_request(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email'].strip().lower()

            # find user
            found_user = None
            for user in CustomUser.objects.all():
                if user.email.lower() == email.lower():
                    found_user = user
                    break
            
            if found_user:
                reset_url = request.build_absolute_uri(
                    reverse('password_reset_confirm', kwargs={'user_id': found_user.id})
                )

                # send verification email
                send_mail(
                    subject="Password Reset Request",
                    message=f"Click the link below to reset your password:\n\n{reset_url}",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    fail_silently=False,
                )
            
            # show error message
            messages.success(request, "If an account with that email exists, a password reset link has been sent.")
            return redirect('login')
    else:
        form = PasswordResetForm()

    return render(request, 'accounts/password_reset.html', {'form': form})