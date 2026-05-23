from django.shortcuts import render
from shipment.models import Shipment


def alerts(request):

    shipments = Shipment.objects.all()

    critical_alerts = []
    warning_alerts = []

    for shipment in shipments:

        # HIGH RISK
        if shipment.risk == "High":

            critical_alerts.append({
                'shipment_id': shipment.shipment_id,
                'message': f"{shipment.origin} to {shipment.destination} route has high delay probability.",
                'action': "Immediate route diversion recommended.",
                'time': shipment.departure,
            })

        # MEDIUM RISK
        elif shipment.risk == "Medium":

            warning_alerts.append({
                'shipment_id': shipment.shipment_id,
                'message': f"{shipment.origin} to {shipment.destination} may experience delays.",
                'time': shipment.departure,
            })

    context = {

        'critical_alerts': critical_alerts,
        'warning_alerts': warning_alerts,

        'critical_count': len(critical_alerts),
        'warning_count': len(warning_alerts),
    }

    return render(
        request,
        'alerts/alerts.html',
        context
    )