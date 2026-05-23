from django.urls import path

from . import api_views
from . import views

urlpatterns = [

    path('',views.analytics_dashboard, name='analytics'),
    path(
        'api/',
        api_views.analytics_api,
        name='analytics_api'
    ),

]