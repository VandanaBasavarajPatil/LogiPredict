from django.urls import path

from . import api_views
from . import views

urlpatterns = [

    path(
        '',
        views.alerts,
        name='alerts'
    ),
    path(
        'api/',
        api_views.alerts_api,
        name='alerts_api'
    ),

]