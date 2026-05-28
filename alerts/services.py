from .models import Alert


#internal helper
def _upsert_alert(shipment_id, alert_type, title, message, level, ai_action=""):
 
    exists = Alert.objects.filter(
        shipment_id_ref=shipment_id,
        title__startswith=f"[{alert_type}]",
        acknowledged=False,
    ).exists()
    if not exists:
        Alert.objects.create(
            shipment_id_ref=shipment_id,
            title=f"[{alert_type}] {title}",
            message=message,
            level=level,
            ai_action=ai_action or "Review shipment and take corrective action.",
        )
        print(f"[Alerts] Created '{alert_type}' alert for {shipment_id}")


def _dismiss_resolved(shipment_id, alert_type):
    """Auto-acknowledge an alert when its condition is no longer true."""
    Alert.objects.filter(
        shipment_id_ref=shipment_id,
        title__startswith=f"[{alert_type}]",
        acknowledged=False,
    ).update(acknowledged=True)


# public API
def generate_alerts_for_shipment(shipment):
    """
    Main entry point. Call after any shipment save / telemetry update.
    Generates or resolves all alert types based on current shipment data.
    """
    sid = shipment.shipment_id

    # HIGH RISK ALERT 
    is_high_risk = (
        shipment.risk_score >= 60
        or shipment.risk in ("High", "Critical")
        or shipment.status in ("Delayed", "At Risk", "AT RISK")
    )
    if is_high_risk:
        _upsert_alert(
            shipment_id=sid,
            alert_type="HIGH_RISK",
            title=f"High Risk Alert - {sid}",
            message=(
                f"Shipment {sid} flagged as {shipment.risk} Risk. "
                f"Risk Score: {shipment.risk_score:.1f}%. "
                f"Status: {shipment.status}."
            ),
            level="critical" if shipment.risk_score >= 75 or shipment.risk == "Critical" else "warning",
            ai_action="Immediate route diversion recommended. Contact dispatcher.",
        )
    else:
        _dismiss_resolved(sid, "HIGH_RISK")

    # TRAFFIC CONGESTION ALERT 
    traffic_delay = _parse_traffic_delay(shipment.on)
    is_congested = traffic_delay >= 2.0

    if is_congested:
        _upsert_alert(
            shipment_id=sid,
            alert_type="TRAFFIC",
            title=f"Traffic Congestion Alert - {sid}",
            message=(
                f"Heavy traffic detected along route for shipment {sid}, "
                f"causing an estimated {traffic_delay:.1f}h delay."
            ),
            level="critical" if traffic_delay >= 5.0 else "warning",
            ai_action="Dynamic re-routing recommended. Notify recipient of delay.",
        )
    else:
        _dismiss_resolved(sid, "TRAFFIC")


    weather_flags = _check_weather(
        shipment.origin_weather,
        shipment.destination_weather,
        shipment.origin_temp,
        shipment.destination_temp,
    )
    if weather_flags["triggered"]:
        _upsert_alert(
            shipment_id=sid,
            alert_type="WEATHER",
            title=f"Extreme Weather Alert - {sid}",
            message=(
                f"Adverse weather detected for shipment {sid}. "
                f"Origin: {shipment.origin_weather} ({shipment.origin_temp:.1f}°C). "
                f"Destination: {shipment.destination_weather} ({shipment.destination_temp:.1f}°C). "
                f"Condition: {weather_flags['reason']}."
            ),
            level="critical" if weather_flags["severe"] else "warning",
            ai_action="Ensure cargo protection. Reduce transit speed in affected zones.",
        )
    else:
        _dismiss_resolved(sid, "WEATHER")


    from django.utils import timezone
    is_overdue = (
        shipment.eta is not None
        and shipment.eta < timezone.now().date()
        and shipment.status not in ("Delivered", "DELIVERED")
    )
    if is_overdue:
        _upsert_alert(
            shipment_id=sid,
            alert_type="OVERDUE",
            title=f"Delivery Overdue - {sid}",
            message=(
                f"Shipment {sid} has passed its ETA ({shipment.eta}) "
                f"and has not been marked delivered."
            ),
            level="critical",
            ai_action="Contact carrier immediately. Update ETA or escalate.",
        )
    else:
        _dismiss_resolved(sid, "OVERDUE")




def _parse_traffic_delay(on_field: str) -> float:
    """Extract traffic_delay hours from shipment.on field."""
    if not on_field or "traffic_delay:" not in on_field:
        return 0.0
    try:
        for part in on_field.split("|"):
            if "traffic_delay:" in part:
                return float(part.split(":")[1].strip().replace("h", ""))
    except Exception:
        pass
    return 0.0


def _check_weather(origin_w, dest_w, origin_t, dest_t) -> dict:
    ow = (origin_w or "").lower()
    dw = (dest_w or "").lower()

    severe_keywords = ["thunderstorm", "storm", "squall", "tornado", "hurricane",
                       "heavy rain", "blizzard", "flood"]
    moderate_keywords = ["rain", "drizzle", "shower", "snow", "haze", "fog",
                         "mist", "smoke", "dust"]

    is_severe = any(kw in ow or kw in dw for kw in severe_keywords)
    is_moderate = any(kw in ow or kw in dw for kw in moderate_keywords)
    is_hot = origin_t > 40 or dest_t > 40

    if is_severe:
        return {"triggered": True, "severe": True, "reason": "Severe storm/flood conditions"}
    if is_moderate:
        return {"triggered": True, "severe": False, "reason": "Rain/fog/haze along route"}
    if is_hot:
        return {"triggered": True, "severe": False, "reason": f"Extreme heat (>{max(origin_t, dest_t):.0f}°C)"}

    return {"triggered": False, "severe": False, "reason": ""}
