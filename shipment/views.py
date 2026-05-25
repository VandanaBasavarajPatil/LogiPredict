# shipment/views.py

from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect

from .forms import ShipmentForm
from .models import Shipment
from .services import predict_delay

import requests
from django.conf import settings


# ==========================================
# GOOGLE MAPS - GET LATITUDE & LONGITUDE
# ==========================================

def get_coordinates(city):
    from .maps_service import get_coordinates as get_coords_from_service
    coords = get_coords_from_service(city)
    return (coords['lat'], coords['lng'])


# ==========================================
# SHIPMENT LIST PAGE
# ==========================================


def create_shipment(request):

    shipments = Shipment.objects.all().order_by('-created_at')

    # Update telemetry for active shipments
    from .services import update_shipment_telemetry
    for shipment in shipments:
        try:
            update_shipment_telemetry(shipment)
        except Exception as e:
            print(f"[Telemetry Warning] {e}")

    return render(
        request,
        'shipment/create_shipment.html',
        {
            'shipments': shipments
        }
    )


# ==========================================
# ADD NEW SHIPMENT
# ==========================================

def add_shipment(request):

    if request.method == 'POST':

        form = ShipmentForm(request.POST)

        if form.is_valid():

            shipment = form.save(commit=False)

            # ==================================
            # GET ORIGIN COORDINATES
            # ==================================

            origin_lat, origin_lng = get_coordinates(
                shipment.origin
            )

            # ==================================
            # GET DESTINATION COORDINATES
            # ==================================

            dest_lat, dest_lng = get_coordinates(
                shipment.destination
            )

            # ==================================
            # SAVE MAP DATA
            # ==================================

            shipment.origin_lat = origin_lat
            shipment.origin_lng = origin_lng

            shipment.dest_lat = dest_lat
            shipment.dest_lng = dest_lng

            # Current location starts at origin

            shipment.current_lat = origin_lat
            shipment.current_lng = origin_lng

            # ==================================
            # SAVE SHIPMENT
            # ==================================

            shipment.save()

            # ==================================
            # AUTOMATICALLY FETCH COORDINATES AND ROUTE DISTANCE
            # ==================================
            try:
                from .route_service import update_shipment_route_data
                update_shipment_route_data(shipment)
            except Exception as e:
                print(f"[Warning] Route update failed: {e}")

            # ==================================
            # AI PREDICTION
            # ==================================

            try:

                predict_delay(shipment)

            except Exception as e:

                print(f"[Warning] Prediction failed: {e}")

            return redirect('shipment')

    else:

        form = ShipmentForm()

    return render(
        request,
        'shipment/add_shipment.html',
        {
            'form': form
        }
    )


# ==========================================
# UPDATE SHIPMENT
# ==========================================

def update_shipment(request, id):

    shipment = get_object_or_404(
        Shipment,
        id=id
    )

    if request.method == 'POST':

        form = ShipmentForm(
            request.POST,
            instance=shipment
        )

        if form.is_valid():

            updated = form.save(commit=False)

            # UPDATE COORDINATES AGAIN

            origin_lat, origin_lng = get_coordinates(
                updated.origin
            )

            dest_lat, dest_lng = get_coordinates(
                updated.destination
            )

            updated.origin_lat = origin_lat
            updated.origin_lng = origin_lng

            updated.dest_lat = dest_lat
            updated.dest_lng = dest_lng

            updated.save()

            # ==================================
            # AUTOMATICALLY FETCH COORDINATES AND ROUTE DISTANCE
            # ==================================
            try:
                from .route_service import update_shipment_route_data
                update_shipment_route_data(updated)
            except Exception as e:
                print(f"[Warning] Route update failed: {e}")

            try:

                predict_delay(updated)

            except Exception as e:

                print(f"[Warning] Re-prediction failed: {e}")

            return redirect('shipment')

    else:

        form = ShipmentForm(instance=shipment)

    return render(
        request,
        'shipment/add_shipment.html',
        {
            'form': form
        }
    )


# ==========================================
# DELETE SHIPMENT
# ==========================================

def delete_shipment(request, id):

    shipment = get_object_or_404(
        Shipment,
        id=id
    )

    shipment.delete()

    return redirect('shipment')


# ==========================================
# LIVE TRACKING API
# ==========================================

def api_tracking_update(request, shipment_id):

    shipment = get_object_or_404(
        Shipment,
        shipment_id=shipment_id
    )

    from .services import update_shipment_telemetry
    try:
        update_shipment_telemetry(shipment)
    except Exception as e:
        print(f"[Telemetry Warning] {e}")

    return JsonResponse({

        'shipment_id': shipment.shipment_id,

        'current_lat': shipment.current_lat,

        'current_lng': shipment.current_lng,

        'status': shipment.status,

    })


# ==========================================
# WEATHER TEST API
# ==========================================

def test_weather(request):

    from .weather_service import get_weather

    data = get_weather("Mumbai")

    return HttpResponse(
        f"Weather OK: {data}"
    )