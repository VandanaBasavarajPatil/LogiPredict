from django.shortcuts import render
from django.db.models import Avg, Q
from shipment.models import Shipment
from alerts.models import Alert
from shipment.services import update_shipment_telemetry
from django.contrib.auth.decorators import login_required


@login_required
def dashboard(request):
    shipments = Shipment.objects.all()
    # Refresh telemetry on page load
    for shipment in shipments:
        try:
            update_shipment_telemetry(shipment)
        except Exception as e:
            print(f"[Telemetry Warning] {e}")
    # 1. Active Shipments: count all shipments
    active_count = shipments.count()
    # 2. At Risk: risk_score >= 50 OR risk in ["MEDIUM", "HIGH"] (or titled/lowercase/choices matching)
    at_risk_count = shipments.filter(
        Q(risk_score__gte=50) | Q(risk__in=["High", "Critical", "MEDIUM", "HIGH", "Medium"])
    ).count()
    # 3. Delivered: status == "DELIVERED"
    delivered_count = shipments.filter(status__in=["DELIVERED", "Delivered"]).count()
    # 4. Avg Risk Score: average of all shipment risk_score values (already out of 100)
    avg_risk = shipments.aggregate(avg=Avg('risk_score'))['avg'] or 0.0
    avg_risk_score = round(avg_risk, 1)
    recent_shipments = shipments.order_by('-created_at')[:5]
    critical_alerts = Alert.objects.filter(
        level='critical', acknowledged=False
    )[:3]
    context = {
        'total_shipments':   active_count,
        'active_count':      active_count,
        'at_risk_shipments': at_risk_count,
        'delivered_today':   delivered_count,
        'avg_risk_score':    avg_risk_score,
        'recent_shipments':  recent_shipments,
        'alerts':            critical_alerts,
        'alert_count':       Alert.objects.filter(acknowledged=False).count(),
    }
    return render(request, 'dashboard.html', context)