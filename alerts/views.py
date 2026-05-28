from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from shipment.models import Shipment
from shipment.services import update_shipment_telemetry, _calculate_traffic_delay
from django.utils import timezone


class LiveAlert:
  
    _id_counter = 0

    def __init__(self, shipment_id_ref, title, message, level, ai_action, created_at):
        LiveAlert._id_counter += 1
        self.id              = LiveAlert._id_counter   # needed for template (acknowledge form)
        self.shipment_id_ref = shipment_id_ref
        self.title           = title
        self.message         = message
        self.level           = level
        self.ai_action       = ai_action
        self.created_at      = created_at


def _build_alerts_for_shipment(shipment, now):

    alerts = []
    sid    = shipment.shipment_id

    origin_w  = (shipment.origin_weather or '').lower()
    dest_w    = (shipment.destination_weather or '').lower()
    origin_t  = shipment.origin_temp or 0.0
    dest_t    = shipment.destination_temp or 0.0
    risk_score = shipment.risk_score or 0.0

    if risk_score >= 60 or shipment.risk in ['High', 'Critical'] or shipment.status == 'Delayed':
        level = 'critical' if (risk_score >= 75 or shipment.risk == 'Critical') else 'warning'
        alerts.append(LiveAlert(
            shipment_id_ref = sid,
            title           = f"High Risk Alert - {sid}",
            message         = (
                f"Shipment {sid} ({shipment.origin} → {shipment.destination}) is flagged as "
                f"{shipment.risk} risk. Current risk score: {risk_score:.1f}%. "
                f"Status: {shipment.status}. Carrier: {shipment.carrier}."
            ),
            level           = level,
            ai_action       = (
                f"Contact carrier {shipment.carrier} immediately. "
                f"Evaluate alternate routes from {shipment.origin} to {shipment.destination}. "
                f"Consider re-routing to reduce delay risk."
            ),
            created_at      = now,
        ))


    if shipment.distance_km:
        traffic_delay, congestion_level = _calculate_traffic_delay(
            shipment.origin_weather,
            shipment.destination_weather,
            shipment.distance_km,
        )
        if traffic_delay > 2.0 or congestion_level in ['Heavy', 'Severe']:
            alerts.append(LiveAlert(
                shipment_id_ref = sid,
                title           = f"Traffic Congestion Alert - {sid}",
                message         = (
                    f"Heavy traffic on route {shipment.origin} → {shipment.destination} "
                    f"for shipment {sid}. "
                    f"Estimated extra delay: {traffic_delay:.1f} hours. "
                    f"Congestion level: {congestion_level}. "
                    f"Route distance: {shipment.distance_km:.0f} km."
                ),
                level           = 'warning',
                ai_action       = (
                    f"Dispatch team should check bypass routes for {shipment.origin}–{shipment.destination}. "
                    f"Driver advised to avoid peak hours to recover the {traffic_delay:.1f}h delay."
                ),
                created_at      = now,
            ))


    BAD_WEATHER = ['storm', 'thunder', 'rain', 'haze', 'drizzle', 'snow', 'flood', 'squall', 'mist']
    has_bad_weather  = any(kw in origin_w or kw in dest_w for kw in BAD_WEATHER)
    has_extreme_temp = origin_t > 40 or dest_t > 40

    if has_bad_weather or has_extreme_temp:
        parts = []
        if has_bad_weather:
            parts.append(
                f"Origin weather: {shipment.origin_weather} ({origin_t:.1f}°C) | "
                f"Destination weather: {shipment.destination_weather} ({dest_t:.1f}°C)"
            )
        if has_extreme_temp:
            parts.append(
                f"Extreme temperatures — Origin: {origin_t:.1f}°C, Destination: {dest_t:.1f}°C"
            )
        alerts.append(LiveAlert(
            shipment_id_ref = sid,
            title           = f"Extreme Weather Alert - {sid}",
            message         = (
                f"Weather risk for shipment {sid} ({shipment.origin} → {shipment.destination}). "
                + " | ".join(parts) + "."
            ),
            level           = 'warning',
            ai_action       = (
                f"Monitor live weather for {shipment.origin} and {shipment.destination}. "
                f"Advise driver to reduce speed. "
                f"Postpone departure if conditions worsen."
            ),
            created_at      = now,
        ))

    return alerts


@login_required
def alerts(request):
    now = timezone.now()
    LiveAlert._id_counter = 0   # reset per request


    active_shipments = Shipment.objects.exclude(status='Delivered')
    for shipment in active_shipments:
        try:
            update_shipment_telemetry(shipment)
        except Exception as e:
            print(f"[Telemetry Warning] {e}")

    # Build in-memory alerts by reading current API data on each shipment
    all_alerts = []
    for shipment in active_shipments:
        all_alerts.extend(_build_alerts_for_shipment(shipment, now))

    critical_list = [a for a in all_alerts if a.level == 'critical']
    warning_list  = [a for a in all_alerts if a.level == 'warning']

    context = {
        'critical_alerts':    critical_list,
        'warning_alerts':     warning_list,
        'critical_count':     len(critical_list),
        'warning_count':      len(warning_list),
        'acknowledged_count': 0,   # no DB — nothing to acknowledge permanently
    }
    return render(request, 'alerts/alerts.html', context)


@login_required
def acknowledge_alert(request, alert_id):

    return redirect('alerts')

