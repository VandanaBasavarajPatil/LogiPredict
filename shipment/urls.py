# shipment/urls.py

from django.urls import path
from . import api_views, views

urlpatterns = [
    path('',                                    views.create_shipment,     name='shipment'),
    path('add/',                                views.add_shipment,        name='add_shipment'),
    path('update/<int:id>/',                    views.update_shipment,     name='update_shipment'),
    path('delete/<int:id>/',                    views.delete_shipment,     name='delete_shipment'),
    path('api/tracking/<str:shipment_id>/',     views.api_tracking_update, name='api_tracking'),
    path('api/',                                api_views.shipment_api,    name='shipment_api'),
    path('api/<int:id>/',                       api_views.shipment_detail_api, name='shipment_detail_api'),
    path('test-weather/',                       views.test_weather,        name='test_weather'),
]