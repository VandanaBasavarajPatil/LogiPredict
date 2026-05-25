# dashboard/views.py

from django.shortcuts import render
from django.db.models import Avg
from shipment.models import Shipment
from alerts.models import Alert


def dashboard(request):
    """Reads everything from DB — no API calls here."""

    shipments = Shipment.objects.all()

    total_shipments = shipments.count()
    at_risk_count   = shipments.filter(risk__in=['High', 'Critical']).count()
    delivered_count = shipments.filter(status='Delivered').count()
    active_count    = shipments.filter(
        status__in=['Pending', 'In Transit', 'At Risk']
    ).count()

    avg_risk = (shipments.aggregate(avg=Avg('risk_score'))['avg'] or 0)
    avg_risk_score = round(avg_risk * 100, 1)

    recent_shipments = shipments.order_by('-created_at')[:5]
    critical_alerts  = Alert.objects.filter(
        level='critical', acknowledged=False
    )[:3]

    context = {
        'total_shipments':   total_shipments,
        'active_count':      active_count,
        'at_risk_shipments': at_risk_count,
        'delivered_today':   delivered_count,
        'avg_risk_score':    avg_risk_score,
        'recent_shipments':  recent_shipments,
        'alerts':            critical_alerts,
        'alert_count':       Alert.objects.filter(acknowledged=False).count(),
    }

    return render(request, 'dashboard.html', context)