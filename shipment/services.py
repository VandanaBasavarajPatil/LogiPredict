from .weather_service import get_weather
from .maps_service import get_route_info


def predict_delay(shipment):
    print(f"[Predict] Starting: {shipment.shipment_id}")

    # Weather API
    origin_data = get_weather(shipment.origin)
    dest_data   = get_weather(shipment.destination)

    # Google Maps API
    route_info    = get_route_info(shipment.origin, shipment.destination)
    distance_km   = route_info['distance_km']
    origin_coords = route_info['origin_coords']
    dest_coords   = route_info['dest_coords']

    # Calculate risk
    risk_score, risk_label = _calculate_combined_risk(
        origin_data['risk_score'],
        dest_data['risk_score'],
        distance_km,
    )

    # Set status
    new_status = 'At Risk' if risk_label in ['High', 'Critical'] else 'In Transit'

    # Save everything
    shipment.risk_score          = round(risk_score, 3)
    shipment.risk                = risk_label
    shipment.status              = new_status
    shipment.distance_km         = distance_km
    shipment.origin_weather      = origin_data['weather']
    shipment.origin_temp         = origin_data['temperature']
    shipment.destination_weather = dest_data['weather']
    shipment.destination_temp    = dest_data['temperature']
    shipment.origin_lat          = origin_coords['lat']
    shipment.origin_lng          = origin_coords['lng']
    shipment.dest_lat            = dest_coords['lat']
    shipment.dest_lng            = dest_coords['lng']
    shipment.current_lat         = route_info['mid_lat']
    shipment.current_lng         = route_info['mid_lng']

    shipment.save(update_fields=[
        'risk_score', 'risk', 'status', 'distance_km',
        'origin_weather', 'origin_temp',
        'destination_weather', 'destination_temp',
        'origin_lat', 'origin_lng',
        'dest_lat', 'dest_lng',
        'current_lat', 'current_lng',
    ])

    print(f"[Predict] Done: {risk_label} ({risk_score:.0%}), {distance_km}km")
    print(f"[Predict] Coords: origin=({origin_coords['lat']},{origin_coords['lng']})")

    _create_alert_if_needed(shipment, risk_score)


def _create_alert_if_needed(shipment, risk_score):
    from alerts.models import Alert
    if risk_score >= 0.5:
        Alert.objects.get_or_create(
            shipment_id_ref=shipment.shipment_id,
            defaults={
                'title':    f"Delay Risk: {shipment.shipment_id}",
                'message':  f"{shipment.origin} to {shipment.destination} has high delay risk.",
                'level':    'critical' if risk_score >= 0.7 else 'warning',
                'ai_action': "Immediate route diversion recommended." if risk_score >= 0.7 else "Monitor closely.",
            }
        )


def _calculate_combined_risk(origin_score, dest_score, distance_km):
    distance_score = min(distance_km / 15000, 1.0)
    combined = round(min(origin_score*0.40 + dest_score*0.25 + distance_score*0.35, 1.0), 3)

    if combined >= 0.70:   label = 'Critical'
    elif combined >= 0.50: label = 'High'
    elif combined >= 0.30: label = 'Medium'
    else:                  label = 'Low'

    return combined, label


def calculate_prediction_score(shipment) -> dict:
    delay_pct = round(shipment.risk_score * 100)
    weather   = shipment.origin_weather.lower() if shipment.origin_weather else ''

    if 'thunder' in weather or 'storm' in weather:
        w_label, w_pct, w_color = 'Critical', 95, 'danger'
    elif 'rain' in weather or 'snow' in weather:
        w_label, w_pct, w_color = 'High', 78, 'warning'
    elif 'cloud' in weather or 'mist' in weather or 'haze' in weather:
        w_label, w_pct, w_color = 'Medium', 45, 'warning'
    else:
        w_label, w_pct, w_color = 'Low', 15, 'success'

    dist = shipment.distance_km or 2000
    if dist > 8000:      p_label, p_pct, p_color = 'Critical', 90, 'danger'
    elif dist > 4000:    p_label, p_pct, p_color = 'High',     65, 'warning'
    elif dist > 1500:    p_label, p_pct, p_color = 'Medium',   40, 'warning'
    else:                p_label, p_pct, p_color = 'Low',      18, 'success'

    if shipment.risk in ['Critical', 'High']:
        ai_rec = "Immediate route diversion recommended."
    elif shipment.risk == 'Medium':
        ai_rec = "Monitor shipment. Consider backup route."
    else:
        ai_rec = "Shipment on track. No action needed."

    return {
        'delay_probability_pct': delay_pct,
        'weather_label': w_label, 'weather_bar_pct': w_pct, 'weather_bar_color': w_color,
        'port_label': p_label,   'port_bar_pct': p_pct,    'port_bar_color': p_color,
        'ai_recommendation': ai_rec,
    }