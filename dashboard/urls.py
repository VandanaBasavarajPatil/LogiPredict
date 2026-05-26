from django.contrib import admin
from django.urls import path
from .views import dashboard
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.dashboard, name='dashboard'),
]