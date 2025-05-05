from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET

@require_GET
@login_required
def home_view(request):
    return render(request, 'app/home.html', {
        'user': request.user
    })