from django.urls import path

from . import api_views
from . import views

urlpatterns = [

    path('',views.prediction,name='prediction'),
    path(
        'api/',
        api_views.predictions_api,
        name='predictions_api'
    ),


]