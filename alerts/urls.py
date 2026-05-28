from django.urls import path
from . import api_views, views

urlpatterns = [
    path('',                           views.alerts,            name='alerts'),
    path('acknowledge/<int:alert_id>/', views.acknowledge_alert, name='acknowledge_alert'),
    path('api/',                       api_views.alerts_api,    name='alerts_api'),
]