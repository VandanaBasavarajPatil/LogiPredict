from rest_framework.decorators import api_view

from rest_framework.response import Response

from shipment.models import Shipment


@api_view(['GET'])
def analytics_api(request):

    total_shipments = Shipment.objects.count()

    delayed_shipments = Shipment.objects.filter(
        status='Delayed'
    ).count()

    at_risk = Shipment.objects.filter(
        risk='High'
    ).count()

    delivered = Shipment.objects.filter(
        status='Delivered'
    ).count()

    data = {

        'total_shipments': total_shipments,

        'delayed_shipments': delayed_shipments,

        'at_risk_shipments': at_risk,

        'delivered_shipments': delivered,

    }

    return Response(data)