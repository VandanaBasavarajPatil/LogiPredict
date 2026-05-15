from django.urls import path
from . import views

urlpatterns = [

    path(
        '',
        views.alerts,
        name='alerts'
    ),

]