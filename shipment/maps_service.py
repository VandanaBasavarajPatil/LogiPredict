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
    "chennai": {"lat": 13.0827, "lng": 80.2707},
    "kolkata": {"lat": 22.5726, "lng": 88.3639},
    "hyderabad": {"lat": 17.3850, "lng": 78.4867},
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
    "vijayawada": {"lat": 16.5062, "lng": 80.6480},
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


def get_route_info(origin: str, destination: str) -> dict:
    from .route_service import geocode_city, calculate_route_distance
    origin_coords = geocode_city(origin) or {'lat': 0.0, 'lng': 0.0}
    dest_coords = geocode_city(destination) or {'lat': 0.0, 'lng': 0.0}
    distance_km = calculate_route_distance(origin, destination)
    
    # Estimate travel duration based on truck avg speed of 55 km/h
    duration_hours = round(distance_km / 55.0, 1)
    
    mid_lat = (origin_coords['lat'] + dest_coords['lat']) / 2
    mid_lng = (origin_coords['lng'] + dest_coords['lng']) / 2

    return {
        'distance_km':    distance_km,
        'duration_hours': duration_hours,
        'origin_coords':  origin_coords,
        'dest_coords':    dest_coords,
        'mid_lat':        mid_lat,
        'mid_lng':        mid_lng,
        'status':         'OK',
    }


def get_coordinates(city: str) -> dict:
    from .route_service import geocode_city
    res = geocode_city(city)
    return res if res is not None else {'lat': 0.0, 'lng': 0.0}


def _get_distance(origin: str, destination: str) -> dict:
    from .route_service import calculate_route_distance
    dist = calculate_route_distance(origin, destination)
    return {
        'distance_km':    dist,
        'duration_hours': round(dist / 55.0, 1),
        'distance_text':  f"{dist} km",
        'status':         'OK',
    }


def _default_distance():
    return {'distance_km': 2000.0, 'duration_hours': 30.0,
            'distance_text': '~2,000 km', 'status': 'FALLBACK'}