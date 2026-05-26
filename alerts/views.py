# alerts/views.py  — FIXED
# Changes:
#   1. Removed destructive Alert.objects.delete() on page load (was destroying audit history)
#   2. acknowledge_alert now only accepts POST (was accepting GET — unsafe)
#   3. Added login_required to acknowledge_alert

from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from .models import Alert
from shipment.models import Shipment
from shipment.services import update_shipment_telemetry
from django.contrib.auth.decorators import login_required


@login_required
def alerts(request):
    # Refresh telemetry for all active shipments
    for shipment in Shipment.objects.exclude(status__in=["Delivered", "DELIVERED"]):
        try:
            update_shipment_telemetry(shipment)
        except Exception as e:
            print(f"[Telemetry Warning] {e}")

    # FIX: REMOVED the destructive Alert.objects.delete() that was running on every page load.
    # Historical alerts for delivered shipments should be kept for audit purposes.
    # If you want cleanup, do it via a management command, not on every page request.

    all_alerts    = Alert.objects.all()
    critical_list = all_alerts.filter(level='critical', acknowledged=False)
    warning_list  = all_alerts.filter(level='warning',  acknowledged=False)

    context = {
        'critical_alerts': critical_list,
        'warning_alerts':  warning_list,
        'critical_count':  critical_list.count(),
        'warning_count':   warning_list.count(),
        # Pass all acknowledged alerts count for audit visibility
        'acknowledged_count': Alert.objects.filter(acknowledged=True).count(),
    }
    return render(request, 'alerts/alerts.html', context)


# FIX: @require_POST ensures only POST requests can acknowledge (not GET)
# This prevents accidental acknowledgement from browser pre-fetching
@login_required
@require_POST
def acknowledge_alert(request, alert_id):
    alert = get_object_or_404(Alert, id=alert_id)
    alert.acknowledged = True
    alert.save()
    return redirect('alerts')
