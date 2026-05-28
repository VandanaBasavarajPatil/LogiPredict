import requests
from django.conf import settings


def get_weather(city: str) -> dict:
    url    = "https://api.openweathermap.org/data/2.5/weather"
    params = {'q': city, 'appid': settings.OPENWEATHER_API_KEY}

    try:
        response = requests.get(url, params=params, timeout=8)

        if response.status_code != 200:
            print(f"[Weather] Error {response.status_code} for {city}")
            return _default_weather(city)

        data         = response.json()
        weather_main = data['weather'][0]['main']
        temp_celsius = round(data['main']['temp'] - 273.15, 1)
        humidity     = data['main']['humidity']
        wind_speed   = data['wind']['speed']
        rain_mm      = data.get('rain', {}).get('1h', 0.0)

        risk_label, risk_score = _calculate_risk(temp_celsius, humidity, wind_speed, rain_mm, weather_main, data['weather'][0]['description'])
        print(f"[Weather] {city}: {weather_main} {temp_celsius} C risk={risk_label}")

        return {
            'city': city, 'weather': weather_main,
            'description': data['weather'][0]['description'],
            'temperature': temp_celsius, 'humidity': humidity,
            'wind_speed': wind_speed, 'rain_mm': rain_mm,
            'risk': risk_label, 'risk_score': risk_score,
        }

    except Exception as e:
        print(f"[Weather] Exception for {city}: {e}")
        return _default_weather(city)


def _calculate_risk(temp, humidity, wind_speed, rain_mm, weather_main, description=""):
    score = 0.0
    desc_lower = description.lower()
    weather_lower = weather_main.lower()
    

    is_storm = any(kw in desc_lower or kw in weather_lower for kw in ['thunderstorm', 'squall', 'tornado', 'storm', 'heavy rain'])
    is_rain = any(kw in desc_lower or kw in weather_lower for kw in ['rain', 'drizzle', 'shower', 'snow']) and not is_storm
    is_fog = any(kw in desc_lower or kw in weather_lower for kw in ['fog', 'haze', 'mist', 'smoke'])
    is_heavy_clouds = any(kw in desc_lower or kw in weather_lower for kw in ['overcast', 'broken clouds'])
    
    if is_storm:
        score += 0.35
    elif is_rain:
        score += 0.20
    elif is_fog:
        score += 0.15
    elif is_heavy_clouds:
        score += 0.08
        
    # Wind Speed
    if wind_speed > 15:
        score += 0.10
    elif wind_speed > 8:
        score += 0.05
        
    # Temperature & Heat
    if temp > 40 or temp < -10:
        score += 0.08
    elif temp > 35 or temp < 0:
        score += 0.04
        
    # Humidity
    if humidity > 90:
        score += 0.05
        
    # Limit weather risk score to maximum of 0.5
    weather_risk_score = min(score, 0.5)
    
    if weather_risk_score >= 0.4:
        label = 'Critical'
    elif weather_risk_score >= 0.25:
        label = 'High'
    elif weather_risk_score >= 0.12:
        label = 'Medium'
    else:
        label = 'Low'
        
    return label, weather_risk_score


def _default_weather(city):
    return {'city': city, 'weather': 'Clear', 'description': 'API unavailable',
            'temperature': 20.0, 'humidity': 50, 'wind_speed': 3.0,'rain_mm': 0.0, 'risk': 'Low', 'risk_score': 0.05}