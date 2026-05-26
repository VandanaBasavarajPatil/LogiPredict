# login/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # Root URL → redirect to login (not a duplicate named 'home')
    path('',         views.login_view,    name='home'),
    path('login/',   views.login_view,    name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/',  views.logout_view,   name='logout'),
]