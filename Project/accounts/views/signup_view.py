from django.shortcuts import render, redirect
from django.core.mail import send_mail
from accounts.forms.signup_form import SignupForm
from django.urls import reverse
from django.conf import settings
from django.views.decorators.http import require_http_methods
import secrets

@require_http_methods(['GET', 'POST'])
def signup_view(request):

    # get form data
    def get_form():
        if request.method == 'POST':
            return SignupForm(request.POST)
        else:
            return SignupForm()

    # create verification email
    def send_verification_code_email(user, verification_code):
        try:
            send_mail(
                'Signup Verification Code',
                f'Your verification code is {verification_code} Enter this in the app to activate your account.',
                settings.EMAIL_HOST_USER,
                [user.email],
                fail_silently=False,
            )
        except Exception as e:
            return False
        return True

    # send the form with data
    def handle_post_request(form):
        user = form.save()
        request.session['pending_user_id'] = user.id
        verification_code = secrets.token_urlsafe(6)
        request.session['verification_code'] = verification_code
        if send_verification_code_email(user, verification_code):
            return redirect(reverse('verify_2fa'))
        else:
            return render(request, 'accounts/signup.html', {'form': form})

    form = get_form()
    if request.method == 'POST':
        if form.is_valid():
            return handle_post_request(form)
        else:
            return render(request, 'accounts/signup.html', {'form': form})
    else:
        return render(request, 'accounts/signup.html', {'form': form})