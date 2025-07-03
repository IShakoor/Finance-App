from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.views.decorators.http import require_http_methods

@require_http_methods(['GET', 'POST'])
def verify_2fa_view(request):
    # fetch id and code from session
    if request.method == 'POST':
        entered_code = request.POST.get('code')
        correct_code = request.session.get('verification_code')

        # error handling
        if not correct_code:
            messages.error(request, "Session expired or invalid request. Please request a new verification code.")
            return redirect('request_2fa')
        
        # check authentication and login
        if entered_code == correct_code:
            user_id = request.session.get('pending_user_id')
            user = get_user_model().objects.get(id=user_id)
            user.is_verified = True
            user.save()
            login(request, user)

            # clean session variables
            if 'verification_code' in request.session:
                del request.session['verification_code']
                del request.session['pending_user_id']
            return redirect('home')

        return render(request, 'accounts/verify_2fa.html', {'error': 'Invalid code. Try again.'})

    return render(request, 'accounts/verify_2fa.html')
