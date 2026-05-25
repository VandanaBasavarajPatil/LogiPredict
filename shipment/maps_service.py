import requests
from django.conf import settings


def get_route_info(origin: str, destination: str) -> dict:
    origin_coords = get_coordinates(origin)
    dest_coords   = get_coordinates(destination)
    distance_data = _get_distance(origin, destination)

    mid_lat = (origin_coords['lat'] + dest_coords['lat']) / 2
    mid_lng = (origin_coords['lng'] + dest_coords['lng']) / 2

    return {
        'distance_km':    distance_data['distance_km'],
        'duration_hours': distance_data['duration_hours'],
        'origin_coords':  origin_coords,
        'dest_coords':    dest_coords,
        'mid_lat':        mid_lat,
        'mid_lng':        mid_lng,
        'status':         distance_data['status'],
    }


def get_coordinates(city: str) -> dict:
    url    = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {'address': city, 'key': settings.GOOGLE_MAPS_API_KEY}

    try:
        response = requests.get(url, params=params, timeout=10)
        data     = response.json()

        if data.get('status') != 'OK':
            print(f"[Maps] Geocode failed: {city} — {data.get('status')}")
            return {'lat': 0.0, 'lng': 0.0}

        loc = data['results'][0]['geometry']['location']
        print(f"[Maps] {city} → {loc['lat']}, {loc['lng']}")
        return {'lat': loc['lat'], 'lng': loc['lng']}

    except Exception as e:
        print(f"[Maps] Error for {city}: {e}")
        return {'lat': 0.0, 'lng': 0.0}


def _get_distance(origin: str, destination: str) -> dict:
    url    = "https://maps.googleapis.com/maps/api/distancematrix/json"
    params = {'origins': origin, 'destinations': destination, 'key': settings.GOOGLE_MAPS_API_KEY}

    try:
        response = requests.get(url, params=params, timeout=10)
        data     = response.json()

        if data.get('status') != 'OK':
            return _default_distance()

        element = data['rows'][0]['elements'][0]
        if element.get('status') != 'OK':
            return _default_distance()

        return {
            'distance_km':    round(element['distance']['value'] / 1000, 1),
            'duration_hours': round(element['duration']['value'] / 3600, 1),
            'distance_text':  element['distance']['text'],
            'status':         'OK',
        }

    except Exception as e:
        print(f"[Maps] Distance error: {e}")
        return _default_distance()


def _default_distance():
    return {'distance_km': 2000.0, 'duration_hours': 30.0,
            'distance_text': '~2,000 km', 'status': 'FALLBACK'}