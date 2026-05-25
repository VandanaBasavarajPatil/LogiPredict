from datetime import timedelta
from django.utils import timezone
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
    duration_hours = route_info['duration_hours']
    origin_coords = route_info['origin_coords']
    dest_coords   = route_info['dest_coords']
    # Calculate traffic delay hours and level
    traffic_delay_hours, congestion_level = _calculate_traffic_delay(
        origin_data['weather'],
        dest_data['weather'],
        distance_km,
    )
    # Calculate combined risk
    weather_score = (origin_data['risk_score'] + dest_data['risk_score']) / 2.0  # max 0.5
    traffic_score = min(traffic_delay_hours / 5.0, 0.3)  # max 0.3
    distance_score = min(distance_km / 5000.0, 0.2)  # max 0.2
    risk_score = min(weather_score + traffic_score + distance_score, 1.0)
    if risk_score >= 0.70:
        risk_label = 'Critical'
    elif risk_score >= 0.50:
        risk_label = 'High'
    elif risk_score >= 0.25:
        risk_label = 'Medium'
    else:
        risk_label = 'Low'
    # Save serialization to 'on' field
    shipment.on = f"duration: {duration_hours:.1f}h | traffic_delay: {traffic_delay_hours:.1f}h | congestion: {congestion_level}"
    # Recalculate ETA (original departure + estimated travel hours + traffic delay hours)
    total_travel_hours = duration_hours + traffic_delay_hours
    eta_datetime = shipment.departure + timedelta(hours=total_travel_hours)
    shipment.eta = eta_datetime.date()
    # Determine status initially based on departure time
    now = timezone.now()
    if shipment.departure > now:
        new_status = 'Pending'
    else:
        new_status = 'At Risk' if risk_label in ['High', 'Critical'] else 'In Transit'
    # Save initial fields
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
    shipment.save(update_fields=[
        'risk_score', 'risk', 'status', 'distance_km',
        'origin_weather', 'origin_temp',
        'destination_weather', 'destination_temp',
        'origin_lat', 'origin_lng',
        'dest_lat', 'dest_lng',
        'on', 'eta'
    ])
    # Run telemetry update to interpolate progress and coordinates
    update_shipment_telemetry(shipment)
    print(f"[Predict] Done: {risk_label} ({risk_score:.0%}), {distance_km}km")
    print(f"[Predict] Coords: origin=({origin_coords['lat']},{origin_coords['lng']})")
    # Generate Alerts
    _create_alerts(shipment, weather_score, traffic_delay_hours, congestion_level)
def _calculate_traffic_delay(origin_weather, dest_weather, distance_km):
    traffic_delay = 0.0
    
    # 1. Weather impact on traffic (Storm adds 3.0h, rain adds 1.5h, fog adds 1.0h)
    for w in [origin_weather.lower(), dest_weather.lower()]:
        if any(kw in w for kw in ['thunder', 'storm', 'squall', 'tornado', 'heavy rain']):
            traffic_delay += 3.0
        elif any(kw in w for kw in ['rain', 'drizzle', 'shower', 'snow']):
            traffic_delay += 1.5
        elif any(kw in w for kw in ['fog', 'haze', 'mist', 'smoke']):
            traffic_delay += 1.0
    # 2. Distance accumulation (e.g., 0.5 hours for every 500 km)
    traffic_delay += (distance_km / 500.0) * 0.5
    # Determine congestion level
    if traffic_delay >= 5.0:
        level = 'Severe'
    elif traffic_delay >= 3.0:
        level = 'Heavy'
    elif traffic_delay >= 1.5:
        level = 'Moderate'
    else:
        level = 'Low'
    return round(traffic_delay, 1), level
def _create_alerts(shipment, weather_score, traffic_delay, congestion_level):
    from alerts.models import Alert
    
    # 1. Weather Alerts
    weather_desc = f"{shipment.origin_weather} (Origin) / {shipment.destination_weather} (Destination)"
    origin_w = shipment.origin_weather.lower()
    dest_w = shipment.destination_weather.lower()
    
    if any(kw in origin_w or kw in dest_w for kw in ['thunder', 'storm', 'squall', 'tornado', 'heavy rain']):
        Alert.objects.get_or_create(
            shipment_id_ref=shipment.shipment_id,
            title=f"Severe Storm Alert - {shipment.shipment_id}",
            defaults={
                'message': f"Severe storm conditions detected along route. Weather: {weather_desc}.",
                'level': 'critical',
                'ai_action': "High delay risk. Advise driver to park in a safe zone until the storm subsides."
            }
        )
    elif any(kw in origin_w or kw in dest_w for kw in ['rain', 'drizzle', 'shower', 'snow']):
        Alert.objects.get_or_create(
            shipment_id_ref=shipment.shipment_id,
            title=f"Rain Warning - {shipment.shipment_id}",
            defaults={
                'message': f"Rain conditions detected. Weather: {weather_desc}.",
                'level': 'warning',
                'ai_action': "Reduce transit speed. Monitor wet road conditions."
            }
        )
    if shipment.origin_temp > 40 or shipment.destination_temp > 40:
        Alert.objects.get_or_create(
            shipment_id_ref=shipment.shipment_id,
            title=f"Extreme Heat Warning - {shipment.shipment_id}",
            defaults={
                'message': f"Extreme heat detected along route: {weather_desc}. Origin temp: {shipment.origin_temp}°C, Destination temp: {shipment.destination_temp}°C.",
                'level': 'warning',
                'ai_action': "Ensure temperature-controlled cargo storage is operational."
            }
        )
    # 2. Traffic Congestion Alerts
    if congestion_level in ['Heavy', 'Severe']:
        Alert.objects.get_or_create(
            shipment_id_ref=shipment.shipment_id,
            title=f"Traffic Congestion Alert - {shipment.shipment_id}",
            defaults={
                'message': f"High congestion ({congestion_level}) detected along route, causing {traffic_delay:.1f} hours delay.",
                'level': 'critical' if congestion_level == 'Severe' else 'warning',
                'ai_action': "Dynamic routing recommended to bypass urban bottleneck zones."
            }
        )
    # 3. AI Risk Alerts
    if shipment.risk in ['High', 'Critical']:
        Alert.objects.get_or_create(
            shipment_id_ref=shipment.shipment_id,
            title=f"High Risk Alert - {shipment.shipment_id}",
            defaults={
                'message': f"Shipment {shipment.shipment_id} is flagged at {shipment.risk} risk. Risk Score: {shipment.risk_score:.0%}.",
                'level': 'critical' if shipment.risk == 'Critical' else 'warning',
                'ai_action': "Dispatching backup route recommendations. Contact operator."
            }
        )
def update_shipment_telemetry(shipment):
    # Only simulate progress if shipment is not delivered
    if shipment.status == 'Delivered' or shipment.progress >= 100:
        return
    # Extract duration and traffic delay from the serialized 'on' field
    duration_hours = 30.0
    traffic_delay = 0.0
    if shipment.on and "duration:" in shipment.on:
        try:
            parts = shipment.on.split('|')
            for part in parts:
                if 'duration:' in part:
                    duration_hours = float(part.split(':')[1].strip().replace('h', ''))
                elif 'traffic_delay:' in part:
                    traffic_delay = float(part.split(':')[1].strip().replace('h', ''))
        except Exception as e:
            print(f"[Telemetry] Parse error for shipment {shipment.shipment_id}: {e}")
    total_travel_hours = duration_hours + traffic_delay
    if total_travel_hours <= 0:
        total_travel_hours = 1.0
    now = timezone.now()
    departure = shipment.departure
    elapsed_time = now - departure
    elapsed_hours = elapsed_time.total_seconds() / 3600.0
    if elapsed_hours < 0:
        # Future shipment
        shipment.progress = 0
        shipment.current_lat = shipment.origin_lat
        shipment.current_lng = shipment.origin_lng
        shipment.status = 'Pending'
        shipment.save(update_fields=['progress', 'current_lat', 'current_lng', 'status'])
        return
    progress = min(int((elapsed_hours / total_travel_hours) * 100), 100)
    shipment.progress = progress
    if progress >= 100:
        shipment.current_lat = shipment.dest_lat
        shipment.current_lng = shipment.dest_lng
        shipment.status = 'Delivered'
    else:
        fraction = progress / 100.0
        shipment.current_lat = shipment.origin_lat + (shipment.dest_lat - shipment.origin_lat) * fraction
        shipment.current_lng = shipment.origin_lng + (shipment.dest_lng - shipment.origin_lng) * fraction
        
        # If in-progress, assign status dynamically
        shipment.status = 'At Risk' if shipment.risk in ['High', 'Critical'] else 'In Transit'
    shipment.save(update_fields=['progress', 'current_lat', 'current_lng', 'status'])
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
    