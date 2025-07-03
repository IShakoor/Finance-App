from django.urls import path
from main.views import *

urlpatterns = [
path('', home_view, name='home'),
]