import math
import requests
from django.conf import settings

CITY_COORDINATES = {
    # Indian Cities/Hubs
    "mumbai": {"lat": 19.0760, "lng": 72.8777},
    "delhi": {"lat": 28.7041, "lng": 77.1025},
    "dehli": {"lat": 28.7041, "lng": 77.1025},
    "new delhi": {"lat": 28.6139, "lng": 77.2090},
    "bangalore": {"lat": 12.9716, "lng": 77.5946},
    "bengaluru": {"lat": 12.9716, "lng": 77.5946},
    "mysuru": {"lat": 12.2958, "lng": 76.6394},
    "mysore": {"lat": 12.2958, "lng": 76.6394},
    "hyderabad": {"lat": 17.3850, "lng": 78.4867},
    "vijayawada": {"lat": 16.5062, "lng": 80.6480},
    "chennai": {"lat": 13.0827, "lng": 80.2707},
    "kolkata": {"lat": 22.5726, "lng": 88.3639},
    "pune": {"lat": 18.5204, "lng": 73.8567},
    "ahmedabad": {"lat": 23.0225, "lng": 72.5714},
    "jaipur": {"lat": 26.9124, "lng": 75.7873},
    "surat": {"lat": 21.1702, "lng": 72.8311},
    "lucknow": {"lat": 26.8467, "lng": 80.9462},
    "nagpur": {"lat": 21.1458, "lng": 79.0882},
    "patna": {"lat": 25.5941, "lng": 85.1376},
    "indore": {"lat": 22.7196, "lng": 75.8577},
    "thane": {"lat": 19.2183, "lng": 72.9781},
    "bhopal": {"lat": 23.2599, "lng": 77.4126},
    "visakhapatnam": {"lat": 17.6868, "lng": 83.2185},
    "vadodara": {"lat": 22.3072, "lng": 73.1812},
    "ghaziabad": {"lat": 28.6692, "lng": 77.4538},
    "ludhiana": {"lat": 30.9010, "lng": 75.8573},
    "agra": {"lat": 27.1767, "lng": 78.0081},
    "nashik": {"lat": 19.9975, "lng": 73.7898},
    "faridabad": {"lat": 28.4089, "lng": 77.3178},
    "meerut": {"lat": 28.9845, "lng": 77.7064},
    "rajkot": {"lat": 22.3039, "lng": 70.8022},
    "varanasi": {"lat": 25.3176, "lng": 82.9739},
    "srinagar": {"lat": 34.0837, "lng": 74.7973},
    "amritsar": {"lat": 31.6340, "lng": 74.8723},
    "navi mumbai": {"lat": 19.0330, "lng": 73.0297},
    "ranchi": {"lat": 23.3441, "lng": 85.3096},
    "coimbatore": {"lat": 11.0168, "lng": 76.9558},
    "jabalpur": {"lat": 22.1760, "lng": 79.9300},
    "gwalior": {"lat": 26.2183, "lng": 78.1828},
    "madurai": {"lat": 9.9252, "lng": 78.1198},
    "guwahati": {"lat": 26.1158, "lng": 91.7086},
    "hubli": {"lat": 15.3647, "lng": 75.1240},
    "kochi": {"lat": 9.9312, "lng": 76.2673},
    "trivandrum": {"lat": 8.5241, "lng": 76.9366},
    "thiruvananthapuram": {"lat": 8.5241, "lng": 76.9366},

    # International Cities/Hubs
    "new york": {"lat": 40.7128, "lng": -74.0060},
    "london": {"lat": 51.5074, "lng": -0.1278},
    "tokyo": {"lat": 35.6762, "lng": 139.6503},
    "singapore": {"lat": 1.3521, "lng": 103.8198},
    "dubai": {"lat": 25.2048, "lng": 55.2708},
    "shanghai": {"lat": 31.2304, "lng": 121.4737},
    "sydney": {"lat": -33.8688, "lng": 151.2093},
    "paris": {"lat": 48.8566, "lng": 2.3522},
    "hong kong": {"lat": 22.3193, "lng": 114.1694},
    "los angeles": {"lat": 34.0522, "lng": -118.2437},
    "chicago": {"lat": 41.8781, "lng": -87.6298},
    "frankfurt": {"lat": 50.1109, "lng": 8.6821},
}


def geocode_city(city_name: str) -> dict:
    if not city_name:
        return None

    city_clean = city_name.strip()
    city_key = city_clean.lower()

    # Try Google Geocoding first
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        'address': city_clean,
        'key': getattr(settings, 'GOOGLE_MAPS_API_KEY', '')
    }

    try:
        response = requests.get(url, params=params, timeout=5)
        data = response.json()
        if data.get('status') == 'OK':
            loc = data['results'][0]['geometry']['location']
            print(f"[Route Service] Geocoded '{city_name}' -> ({loc['lat']}, {loc['lng']}) via Google")
            return {'lat': loc['lat'], 'lng': loc['lng']}
    except Exception as e:
        print(f"[Route Service] Google Geocoding error for '{city_name}': {e}")

    # Fallback to local dictionary
    if city_key in CITY_COORDINATES:
        coords = CITY_COORDINATES[city_key]
        print(f"[Route Service] Geocoded '{city_name}' -> ({coords['lat']}, {coords['lng']}) via Fallback Dictionary")
        return coords

    # Partial matching fallback
    for key, coords in CITY_COORDINATES.items():
        if key in city_key or city_key in key:
            print(f"[Route Service] Geocoded '{city_name}' (matched '{key}') -> ({coords['lat']}, {coords['lng']}) via Partial Fallback")
            return coords

    print(f"[Route Service] Geocoding failed for '{city_name}'")
    return None


def calculate_route_distance(origin: str, destination: str) -> float:
    # 1. Geocode both origin and destination
    origin_coords = geocode_city(origin)
    dest_coords = geocode_city(destination)

    if not origin_coords or not dest_coords:
        return 2000.0

    # 2. Try Google Distance Matrix API
    google_dist = _query_google_distance_matrix(origin, destination)
    if google_dist is not None:
        print(f"[Route Service] Distance between {origin} and {destination} is {google_dist} km (via Google)")
        return google_dist

    # 3. Try OSRM routing API using coordinates
    osrm_dist = _query_osrm_distance(origin_coords, dest_coords)
    if osrm_dist is not None:
        print(f"[Route Service] Distance between {origin} and {destination} is {osrm_dist} km (via OSRM)")
        return osrm_dist

    # 4. Fallback to Haversine distance with 1.25 road detour factor
    haversine_dist = _calculate_haversine_distance(origin_coords, dest_coords)
    road_est = round(haversine_dist * 1.25, 1)
    print(f"[Route Service] Distance between {origin} and {destination} is {road_est} km (via Haversine Fallback)")
    return road_est


def update_shipment_route_data(shipment):
    print(f"[Route Service] Automatically updating route data for shipment {shipment.shipment_id}")

    origin_coords = geocode_city(shipment.origin)
    dest_coords = geocode_city(shipment.destination)

    if origin_coords:
        shipment.origin_lat = origin_coords['lat']
        shipment.origin_lng = origin_coords['lng']
    if dest_coords:
        shipment.dest_lat = dest_coords['lat']
        shipment.dest_lng = dest_coords['lng']

    # Set current location to origin if not set
    if origin_coords and (shipment.current_lat == 0.0 or shipment.current_lat == origin_coords['lat']) and (shipment.current_lng == 0.0 or shipment.current_lng == origin_coords['lng']):
        shipment.current_lat = origin_coords['lat']
        shipment.current_lng = origin_coords['lng']

    distance_km = calculate_route_distance(shipment.origin, shipment.destination)
    shipment.distance_km = distance_km

    shipment.save(update_fields=[
        'origin_lat', 'origin_lng',
        'dest_lat', 'dest_lng',
        'current_lat', 'current_lng',
        'distance_km'
    ])
    print(f"[Route Service] Saved route data for {shipment.shipment_id}: {distance_km} km")


def _query_google_distance_matrix(origin: str, destination: str) -> float:
    url = "https://maps.googleapis.com/maps/api/distancematrix/json"
    params = {
        'origins': origin,
        'destinations': destination,
        'key': getattr(settings, 'GOOGLE_MAPS_API_KEY', '')
    }
    try:
        response = requests.get(url, params=params, timeout=5)
        data = response.json()
        if data.get('status') == 'OK':
            element = data['rows'][0]['elements'][0]
            if element.get('status') == 'OK':
                return round(element['distance']['value'] / 1000.0, 1)
    except Exception as e:
        print(f"[Route Service] Google Distance Matrix error: {e}")
    return None


def _query_osrm_distance(origin_coords: dict, dest_coords: dict) -> float:
    # OSRM expects longitude, latitude
    url = f"http://router.project-osrm.org/route/v1/driving/{origin_coords['lng']},{origin_coords['lat']};{dest_coords['lng']},{dest_coords['lat']}"
    params = {'overview': 'false'}
    try:
        response = requests.get(url, params=params, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('code') == 'Ok' and data.get('routes'):
                distance_meters = data['routes'][0]['distance']
                return round(distance_meters / 1000.0, 1)
    except Exception as e:
        print(f"[Route Service] OSRM routing API error: {e}")
    return None


def _calculate_haversine_distance(c1: dict, c2: dict) -> float:
    R = 6371.0 # Earth radius in km
    lat1, lon1 = math.radians(c1['lat']), math.radians(c1['lng'])
    lat2, lon2 = math.radians(c2['lat']), math.radians(c2['lng'])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c
