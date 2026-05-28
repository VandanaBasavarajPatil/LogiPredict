def calculate_weather_risk(weather):
    if not weather:
        return 0.10
    weather = weather.lower()
    
    # Weather rules: Clouds/Clear -> Low (0.10); Rain/Storm/Flood -> High (0.85); Heat -> Medium (0.45)
    if any(x in weather for x in ['storm', 'thunder', 'flood', 'rain', 'drizzle', 'shower', 'snow']):
        return 0.85
    elif any(x in weather for x in ['hot', 'heat', 'sunny', 'warm']):
        return 0.45
    elif any(x in weather for x in ['cloud', 'overcast', 'clear', 'fair', 'sky']):
        return 0.10
    return 0.10
def calculate_distance_risk(distance):
    # Distance rules: 0-200 km -> low (0.15); 200-800 km -> medium (0.50); 800+ km -> high (0.85)
    if distance > 800:
        return 0.85
    elif distance > 200:
        return 0.50
    return 0.15
def calculate_traffic_risk(delay_hours):
  
    if delay_hours > 6:
        return 0.90
    elif delay_hours > 3:
        return 0.65
    elif delay_hours > 1:
        return 0.40
    return 0.15
def calculate_eta_risk(delay_hours):
    if delay_hours > 5:
        return 0.85
    elif delay_hours > 2:
        return 0.55
    return 0.20
def calculate_total_risk(weather_risk, traffic_risk, distance_risk, eta_risk):
    score_fraction = (
        traffic_risk * 0.35 +
        weather_risk * 0.20 +
        distance_risk * 0.30 +
        eta_risk * 0.15
    )

    return round(score_fraction * 100, 1)
def get_risk_label(score):
    pct = round(score)

    if pct <= 30:
        return "Low"
    elif pct <= 60:
        return "Medium"
    else:
        return "High"