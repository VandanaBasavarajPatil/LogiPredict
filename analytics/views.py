from django.shortcuts import render
from shipment.models import Shipment
from django.db.models import Count


def analytics_dashboard(request):

    # TOTAL SHIPMENTS
    total_shipments = Shipment.objects.count()

    # DELIVERED
    delivered_shipments = Shipment.objects.filter(
        status="Delivered"
    ).count()

    # AT RISK
    at_risk_shipments = Shipment.objects.filter(
        risk="High"
    ).count()

    # NORMAL
    normal_shipments = Shipment.objects.filter(
        risk="Normal"
    ).count()

    # MEDIUM
    medium_shipments = Shipment.objects.filter(
        risk="Medium"
    ).count()

    # TRANSPORT ANALYTICS
    carrier_stats = Shipment.objects.values(
        'carrier'
    ).annotate(
        total=Count('id')
    )

    # ROUTE ANALYTICS
    route_stats = Shipment.objects.values(
        'origin',
        'destination'
    ).annotate(
        total=Count('id')
    )

    # DELAY PERCENTAGE
    if total_shipments > 0:

        delay_percentage = int(
            (at_risk_shipments / total_shipments) * 100
        )

    else:
        delay_percentage = 0

    context = {

        'total_shipments': total_shipments,

        'delivered_shipments': delivered_shipments,

        'at_risk_shipments': at_risk_shipments,

        'normal_shipments': normal_shipments,

        'medium_shipments': medium_shipments,

        'delay_percentage': delay_percentage,

        'carrier_stats': carrier_stats,

        'route_stats': route_stats,
    }

    return render(
        request,
        'analytics/analytics.html',
        context
    )