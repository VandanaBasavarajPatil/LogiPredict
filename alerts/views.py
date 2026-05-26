from django.shortcuts import render, get_object_or_404, redirect
from .models import Alert
from shipment.models import Shipment
from shipment.services import update_shipment_telemetry
from django.contrib.auth.decorators import login_required

@login_required
def alerts(request):
    # Update telemetry for all shipments to keep positions and status accurate
    for shipment in Shipment.objects.all():
        try:
            update_shipment_telemetry(shipment)
        except Exception as e:
            print(f"[Telemetry Warning] {e}")
    # Purge old alerts for successfully delivered shipments (so old alerts don't persist forever)
    delivered_shipment_ids = Shipment.objects.filter(status__in=['DELIVERED', 'Delivered']).values_list('shipment_id', flat=True)
    Alert.objects.filter(shipment_id_ref__in=delivered_shipment_ids).delete()
    all_alerts    = Alert.objects.all()
    critical_list = all_alerts.filter(level='critical', acknowledged=False)
    warning_list  = all_alerts.filter(level='warning',  acknowledged=False)
    context = {
        'critical_alerts': critical_list,
        'warning_alerts':  warning_list,
        'critical_count':  critical_list.count(),
        'warning_count':   warning_list.count(),
    }
    return render(request, 'alerts/alerts.html', context)
def acknowledge_alert(request, alert_id):
    alert = get_object_or_404(Alert, id=alert_id)
    alert.acknowledged = True
    alert.save()
    return redirect('alerts')