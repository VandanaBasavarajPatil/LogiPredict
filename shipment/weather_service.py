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

        risk_label, risk_score = _calculate_risk(temp_celsius, humidity, wind_speed, rain_mm, weather_main)
        print(f"[Weather] {city}: {weather_main} {temp_celsius}°C risk={risk_label}")

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


def _calculate_risk(temp, humidity, wind_speed, rain_mm, weather_main):
    score = 0.0
    if rain_mm > 10 or weather_main in ['Thunderstorm', 'Tornado']: score += 0.45
    elif rain_mm > 3 or weather_main in ['Rain', 'Drizzle', 'Snow']: score += 0.25
    elif rain_mm > 0: score += 0.10
    if wind_speed > 15: score += 0.30
    elif wind_speed > 8: score += 0.15
    if temp < -10 or temp > 45: score += 0.15
    elif temp < 0 or temp > 38: score += 0.08
    if humidity > 90: score += 0.10
    score = min(score, 1.0)
    if score >= 0.5:    return 'High',   score
    elif score >= 0.25: return 'Medium', score
    else:               return 'Low',    score


def _default_weather(city):
    return {'city': city, 'weather': 'Clear', 'description': 'API unavailable',
            'temperature': 20.0, 'humidity': 50, 'wind_speed': 3.0,
            'rain_mm': 0.0, 'risk': 'Low', 'risk_score': 0.1}