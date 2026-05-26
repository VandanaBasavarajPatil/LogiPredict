from django.shortcuts import render
from shipment.models import Shipment
from django.db.models import Count
from shipment.services import update_shipment_telemetry
from django.contrib.auth.decorators import login_required

@login_required
def analytics_dashboard(request):
    # Refresh telemetry on load
    for shipment in Shipment.objects.all():
        try:
            update_shipment_telemetry(shipment)
        except Exception as e:
            print(f"[Telemetry Warning] {e}")
    # Total shipments count
    total_shipments = Shipment.objects.count()
    # On-Time count: status == "DELIVERED"
    delivered_shipments = Shipment.objects.filter(status__in=["DELIVERED", "Delivered"]).count()
    # Delayed count: delay_probability >= 50 (since delay_probability = max(5, int(risk_score * 0.8)), this matches risk_score >= 62.5)
    delayed_shipments = Shipment.objects.filter(risk_score__gte=62.5).count()
    # Risk Distribution (LOW: 0-30, MEDIUM: 31-60, HIGH: 61-100)
    normal_shipments = Shipment.objects.filter(risk_score__lte=30).count()  # LOW
    medium_shipments = Shipment.objects.filter(risk_score__gt=30, risk_score__lte=60).count()  # MEDIUM
    at_risk_shipments = Shipment.objects.filter(risk_score__gt=60).count()  # HIGH
    # Carrier statistics
    carrier_stats = Shipment.objects.values('carrier').annotate(total=Count('id')).order_by('-total')
    # Top Route statistics
    route_stats = Shipment.objects.values('origin', 'destination').annotate(total=Count('id')).order_by('-total')
    # Delay percentage for the red bar chart
    if total_shipments > 0:
        delay_percentage = int((delayed_shipments / total_shipments) * 100)
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
    return render(request, 'analytics/analytics.html', context)