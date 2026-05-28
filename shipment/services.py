from datetime import timedelta
from django.utils import timezone
from .weather_service import get_weather
from .maps_service import get_route_info
from .risk_engine import (
    calculate_weather_risk,
    calculate_distance_risk,
    calculate_traffic_risk,
    calculate_eta_risk,
    calculate_total_risk,
    get_risk_label
)
def calculate_shipment_status(shipment):
    # Status Automation Rules:
    # DELIVERED: progress >= 100 AND current date >= ETA
    is_delivered = getattr(shipment, 'delivered', False) or shipment.status == 'DELIVERED' or shipment.status == 'Delivered' or (shipment.progress >= 100 and (shipment.eta is None or timezone.now().date() >= shipment.eta))
    if is_delivered:
        return "DELIVERED"
        
    # AT RISK: risk_score >= 70
    if shipment.risk_score >= 70:
        return "AT RISK"
        
    # DELAYED: eta < today
    if shipment.eta and shipment.eta < timezone.now().date():
        return "DELAYED"
        
    # IN TRANSIT: coordinates populated
    if shipment.current_lat and shipment.current_lng:
        return "IN TRANSIT"
        
    # PENDING: default state
    return "PENDING"
def predict_delay(shipment):
    print(f"[Predict] Refined Starting: {shipment.shipment_id}")
    
   
    origin_data = get_weather(shipment.origin)
    dest_data   = get_weather(shipment.destination)
    
 
    route_info    = get_route_info(shipment.origin, shipment.destination)
    distance_km   = route_info['distance_km']
    duration_hours = route_info['duration_hours']
    origin_coords = route_info['origin_coords']
    dest_coords   = route_info['dest_coords']
    

    traffic_delay_hours, congestion_level = _calculate_traffic_delay(
        origin_data['weather'],
        dest_data['weather'],
        distance_km,
    )

    weather_factor = (calculate_weather_risk(origin_data['weather']) + calculate_weather_risk(dest_data['weather'])) / 2.0
    traffic_factor = calculate_traffic_risk(traffic_delay_hours)
    distance_factor = calculate_distance_risk(distance_km)
    eta_factor = calculate_eta_risk(traffic_delay_hours)
    

    risk_score = calculate_total_risk(
        weather_risk=weather_factor,
        traffic_risk=traffic_factor,
        distance_risk=distance_factor,
        eta_risk=eta_factor
    )
    risk_label = get_risk_label(risk_score)
    

    shipment.on = f"duration: {duration_hours:.1f}h | traffic_delay: {traffic_delay_hours:.1f}h | congestion: {congestion_level}"
    

    total_travel_hours = duration_hours + traffic_delay_hours
    eta_datetime = shipment.departure + timedelta(hours=total_travel_hours)
    shipment.eta = eta_datetime.date()
    
    shipment.risk_score          = round(risk_score, 1)
    shipment.risk                = risk_label
    shipment.distance_km         = distance_km
    shipment.origin_weather      = origin_data['weather']
    shipment.origin_temp         = origin_data['temperature']
    shipment.destination_weather = dest_data['weather']
    shipment.destination_temp    = dest_data['temperature']
    shipment.origin_lat          = origin_coords['lat']
    shipment.origin_lng          = origin_coords['lng']
    shipment.dest_lat            = dest_coords['lat']
    shipment.dest_lng            = dest_coords['lng']
    

    shipment.status = calculate_shipment_status(shipment)
    shipment.save()
    

    update_shipment_telemetry(shipment)
    

    try:
        from alerts.services import generate_alerts_for_shipment
        generate_alerts_for_shipment(shipment)
    except Exception as e:
        print(f"[Alerts] Generation error: {e}")
    
    print(f"[Predict] Refined Done: {risk_label} ({risk_score:.1f}%), {distance_km}km")
def _calculate_traffic_delay(origin_weather, dest_weather, distance_km):
    traffic_delay = 0.0
    for w in [origin_weather.lower(), dest_weather.lower()]:
        if any(kw in w for kw in ['thunder', 'storm', 'squall', 'tornado', 'heavy rain', 'flood']):
            traffic_delay += 3.0
        elif any(kw in w for kw in ['rain', 'drizzle', 'shower', 'snow']):
            traffic_delay += 1.5
        elif any(kw in w for kw in ['fog', 'haze', 'mist', 'smoke']):
            traffic_delay += 1.0
            
    traffic_delay += (distance_km / 500.0) * 0.5
    
    if traffic_delay >= 5.0:
        level = 'Severe'
    elif traffic_delay >= 3.0:
        level = 'Heavy'
    elif traffic_delay >= 1.5:
        level = 'Moderate'
    else:
        level = 'Low'
        
    return round(traffic_delay, 1), level
def _add_alert_if_not_exists(shipment, title, message, level):
    from alerts.models import Alert
    existing = Alert.objects.filter(
        shipment_id_ref=shipment.shipment_id,
        message=message,
        acknowledged=False
    ).exists()
    
    if not existing:
        Alert.objects.create(
            shipment_id_ref=shipment.shipment_id,
            title=title,
            message=message,
            level=level,
            ai_action="Dynamic route adjustment and dispatcher contact recommended."
        )
def _create_alerts(shipment, weather_score, traffic_delay, congestion_level):
    delay_prob = max(5, int(shipment.risk_score * 0.8))
    

    origin_w = shipment.origin_weather.lower()
    dest_w = shipment.destination_weather.lower()
    
    is_storm = any(kw in origin_w or kw in dest_w for kw in ['thunder', 'storm', 'squall', 'tornado', 'heavy rain'])
    is_flood = any(kw in origin_w or kw in dest_w for kw in ['flood', 'drown', 'submerge'])
    
    alert_lvl = "critical" if shipment.risk_score >= 75 else "warning"
    
    if is_storm:
        msg = f"Severe storm conditions detected along route for {shipment.shipment_id}."
        _add_alert_if_not_exists(shipment, "Severe Storm Alert", msg, alert_lvl)
    elif is_flood:
        msg = f"Potential flooding along the route for {shipment.shipment_id}."
        _add_alert_if_not_exists(shipment, "Flooding Warning", msg, alert_lvl)
        

    if congestion_level in ['Heavy', 'Severe'] or traffic_delay >= 5.0:
        msg = f"Extreme traffic congestion detected along route, causing {traffic_delay:.1f} hours delay."
        _add_alert_if_not_exists(shipment, "Extreme Congestion Alert", msg, alert_lvl)
        

    if delay_prob >= 75:
        msg = f"High probability of late delivery ({delay_prob}% delay chance) for shipment {shipment.shipment_id}."
        _add_alert_if_not_exists(shipment, "High Delay Risk Alert", msg, "critical")
        

    if shipment.risk_score >= 75:
        msg = f"Shipment {shipment.shipment_id} is flagged at CRITICAL risk. Risk Score: {shipment.risk_score:.1f}%."
        _add_alert_if_not_exists(shipment, f"Critical Risk Alert - {shipment.shipment_id}", msg, "critical")
    elif shipment.risk_score >= 50:
        msg = f"Shipment {shipment.shipment_id} is flagged at WARNING risk. Risk Score: {shipment.risk_score:.1f}%."
        _add_alert_if_not_exists(shipment, f"High Risk Alert - {shipment.shipment_id}", msg, "warning")
def update_shipment_telemetry(shipment):
    from django.utils import timezone
    now = timezone.now()
    
    duration_hours = 0.0
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
            print(f"[Telemetry] Parse error: {e}")
            
    total_travel_hours = duration_hours + traffic_delay
    if total_travel_hours <= 0:
        total_travel_hours = 1.0
        
    elapsed_time = now - shipment.departure
    elapsed_hours = elapsed_time.total_seconds() / 3600.0
    
    if elapsed_hours < 0:
        progress = 0
    else:
        progress = min(int((elapsed_hours / total_travel_hours) * 100), 100)
        
    shipment.progress = progress
    
    if progress >= 100:
        shipment.current_lat = shipment.dest_lat
        shipment.current_lng = shipment.dest_lng
    else:
        fraction = progress / 100.0
        shipment.current_lat = shipment.origin_lat + (shipment.dest_lat - shipment.origin_lat) * fraction
        shipment.current_lng = shipment.origin_lng + (shipment.dest_lng - shipment.origin_lng) * fraction
        

    shipment.status = calculate_shipment_status(shipment)
    shipment.save()

    # Re-generate alerts after telemetry update (catches overdue/status changes)
    try:
        from alerts.services import generate_alerts_for_shipment
        generate_alerts_for_shipment(shipment)
    except Exception as e:
        print(f"[Alerts] Telemetry alert error: {e}")
def calculate_prediction_score(shipment) -> dict:
    delay_pct = max(5, int(shipment.risk_score * 0.8))
    weather   = shipment.origin_weather.lower() if shipment.origin_weather else ''
    
    if any(x in weather for x in ['storm', 'thunder', 'flood', 'rain', 'drizzle', 'shower', 'snow']):
        w_label, w_pct, w_color = 'High', 85, 'danger'
    elif any(x in weather for x in ['hot', 'heat', 'sunny', 'warm']):
        w_label, w_pct, w_color = 'Medium', 45, 'warning'
    else:
        w_label, w_pct, w_color = 'Low', 15, 'success'
        
    dist = shipment.distance_km
    if dist > 800:
        p_label, p_pct, p_color = 'High',     85, 'danger'
    elif dist > 200:
        p_label, p_pct, p_color = 'Medium',   50, 'warning'
    else:
        p_label, p_pct, p_color = 'Low',      15, 'success'
        
    if shipment.risk_score >= 70:
        ai_rec = "Immediate route diversion recommended due to high risk."
    elif shipment.risk_score >= 31:
        ai_rec = "Monitor shipment closely and prepare alternative routing."
    else:
        ai_rec = "Shipment on track. Standard routing active."
        
    return {
        'delay_probability_pct': delay_pct,
        'weather_label': w_label, 'weather_bar_pct': w_pct, 'weather_bar_color': w_color,
        'port_label': p_label,   'port_bar_pct': p_pct,    'port_bar_color': p_color,
        'ai_recommendation': ai_rec,
    }