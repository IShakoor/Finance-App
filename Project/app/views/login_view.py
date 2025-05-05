from django.shortcuts import render, redirect
from app.forms.login_form import LoginForm
from app.models.user import CustomUser
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.http import require_http_methods
import secrets

# validate user details and allow login
@require_http_methods(['GET', 'POST'])
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            
            # find user
            found_user = None
            for user in CustomUser.objects.all():
                if user.email.lower() == email.lower():
                    found_user = user
                    break

            if not found_user:
                messages.error(request, "User not found. Please check your email address.")
                return render(request, 'app/login.html', {'form': form})
            
            # Check password after finding the user
            if not found_user.check_password(password):
                messages.error(request, "Invalid password. Please try again.")
                return render(request, 'app/login.html', {'form': form})
            
            # create code & store user details
            verification_code = secrets.token_urlsafe(6)
            request.session['verification_code'] = verification_code
            request.session['pending_user_id'] = found_user.id
            
            # send verification email
            subject = 'Your Login Verification Code'
            message = f'Your verification code is {verification_code}. Enter this in the app to complete your login.'
            from_email = settings.EMAIL_HOST_USER
            to_email = found_user.email
            
            # send the 2FA message
            try:
                send_mail(subject, message, from_email, [to_email], fail_silently=False)
            except Exception as e:
                messages.error(request, f"Failed to send verification email. Please try again. Error: {str(e)}")
                return render(request, 'app/login.html', {'form': form})
            
            return redirect('verify_2fa')
    else:
        form = LoginForm()
    
    return render(request, 'app/login.html', {'form': form})