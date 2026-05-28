import math
import requests
from django.conf import settings


CITY_COORDINATES = {
    "mumbai": {"lat": 19.0760, "lng": 72.8777},
    "delhi": {"lat": 28.7041, "lng": 77.1025},
    "dehli": {"lat": 28.7041, "lng": 77.1025},

    "bengaluru": {"lat": 12.9716, "lng": 77.5946},
    "bangalore": {"lat": 12.9716, "lng": 77.5946},

    "mysuru": {"lat": 12.2958, "lng": 76.6394},
    "mysore": {"lat": 12.2958, "lng": 76.6394},

    "hyderabad": {"lat": 17.3850, "lng": 78.4867},
    "vijayawada": {"lat": 16.5062, "lng": 80.6480},

    "chennai": {"lat": 13.0827, "lng": 80.2707},
    "pune": {"lat": 18.5204, "lng": 73.8567},
}


def geocode_city(city_name):
    """
    Convert city name into coordinates.
    """

    if not city_name:
        return None

    city_key = city_name.strip().lower()

    # Local fallback
    if city_key in CITY_COORDINATES:
        return CITY_COORDINATES[city_key]

    # Google Geocoding API
    try:
        url = "https://maps.googleapis.com/maps/api/geocode/json"

        params = {
            "address": city_name,
            "key": settings.GOOGLE_MAPS_API_KEY
        }

        response = requests.get(url, params=params, timeout=5)
        data = response.json()

        if data.get("status") == "OK":
            location = data["results"][0]["geometry"]["location"]

            return {
                "lat": location["lat"],
                "lng": location["lng"]
            }

    except Exception as e:
        print("Geocoding Error:", e)

    return None


def calculate_route_distance(origin, destination):
    """
    Main route distance calculator.
    Priority:
    1. Google Distance Matrix
    2. OSRM
    3. Haversine fallback
    """

    origin_coords = geocode_city(origin)
    dest_coords = geocode_city(destination)

    if not origin_coords or not dest_coords:
        return 0.0

    # Google Distance Matrix
    google_distance = _query_google_distance(origin, destination)

    if google_distance:
        return google_distance

   
    osrm_distance = _query_osrm_distance(
        origin_coords,
        dest_coords
    )

    if osrm_distance:
        return osrm_distance

  
    haversine = _calculate_haversine_distance(
        origin_coords,
        dest_coords
    )


    return round(haversine * 1.20, 1)


def update_shipment_route_data(shipment):
    """
    Update shipment coordinates and distance.
    """

    origin_coords = geocode_city(shipment.origin)
    dest_coords = geocode_city(shipment.destination)


    if origin_coords:
        shipment.origin_lat = origin_coords["lat"]
        shipment.origin_lng = origin_coords["lng"]

       
        if shipment.current_lat == 0:
            shipment.current_lat = origin_coords["lat"]

        if shipment.current_lng == 0:
            shipment.current_lng = origin_coords["lng"]


    if dest_coords:
        shipment.dest_lat = dest_coords["lat"]
        shipment.dest_lng = dest_coords["lng"]


    shipment.distance_km = calculate_route_distance(
        shipment.origin,
        shipment.destination
    )

    shipment.save()


def _query_google_distance(origin, destination):
    """
    Google Distance Matrix API.
    """

    try:
        url = "https://maps.googleapis.com/maps/api/distancematrix/json"

        params = {
            "origins": origin,
            "destinations": destination,
            "key": settings.GOOGLE_MAPS_API_KEY
        }

        response = requests.get(url, params=params, timeout=5)
        data = response.json()

        if data.get("status") == "OK":

            element = data["rows"][0]["elements"][0]

            if element.get("status") == "OK":

                distance_meters = element["distance"]["value"]

                return round(distance_meters / 1000, 1)

    except Exception as e:
        print("Google Distance API Error:", e)

    return None


def _query_osrm_distance(origin_coords, dest_coords):
    """
    OSRM OpenStreetMap routing fallback.
    """

    try:
        url = (
            f"http://router.project-osrm.org/route/v1/driving/"
            f"{origin_coords['lng']},{origin_coords['lat']};"
            f"{dest_coords['lng']},{dest_coords['lat']}"
        )

        response = requests.get(url, timeout=5)
        data = response.json()

        if data.get("code") == "Ok":

            distance_meters = data["routes"][0]["distance"]

            return round(distance_meters / 1000, 1)

    except Exception as e:
        print("OSRM Error:", e)

    return None


def _calculate_haversine_distance(c1, c2):
    """
    Air distance fallback.
    """

    R = 6371  # Earth radius in KM

    lat1 = math.radians(c1["lat"])
    lon1 = math.radians(c1["lng"])

    lat2 = math.radians(c2["lat"])
    lon2 = math.radians(c2["lng"])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1)
        * math.cos(lat2)
        * math.sin(dlon / 2) ** 2
    )

    c = 2 * math.atan2(
        math.sqrt(a),
        math.sqrt(1 - a)
    )

    return R * c