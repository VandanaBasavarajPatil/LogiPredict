from django.shortcuts import render, get_object_or_404, redirect
from .models import Alert


def alerts(request):
    # Update telemetry for all shipments to trigger any dynamic status/progress alerts
    from shipment.models import Shipment
    from shipment.services import update_shipment_telemetry
    for shipment in Shipment.objects.all():
        try:
            update_shipment_telemetry(shipment)
        except Exception as e:
            print(f"[Telemetry Warning] {e}")

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