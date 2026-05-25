from django.shortcuts import render
from django.conf import settings
from shipment.models import Shipment


def tracking(request):
    shipments = Shipment.objects.all().order_by('-created_at')

    # Update telemetry for all shipments to keep positions and status accurate
    from shipment.services import update_shipment_telemetry
    for shipment in shipments:
        try:
            update_shipment_telemetry(shipment)
        except Exception as e:
            print(f"[Telemetry Warning] {e}")

    selected_id     = request.GET.get('shipment_id')
    active_shipment = None

    if selected_id:
        active_shipment = shipments.filter(shipment_id=selected_id).first()

    if not active_shipment:
        active_shipment = shipments.first()

    context = {
        'shipments':       shipments,
        'active_shipment': active_shipment,
        'google_maps_key': settings.GOOGLE_MAPS_API_KEY,
    }

    return render(request, 'tracking/tracking.html', context)