from django.contrib import admin
from django.urls import path
from .views import dashboard
from . import views

urlpatterns = [
   
    path('', views.dashboard, name='dashboard'),
]