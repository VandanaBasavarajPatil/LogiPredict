import math
import requests
from django.conf import settings


# shipment/route_service.py — REPLACE the CITY_COORDINATES dict

CITY_COORDINATES = {
    # Karnataka
    "bengaluru": {"lat": 12.9716, "lng": 77.5946}, "bangalore": {"lat": 12.9716, "lng": 77.5946},
    "mysuru": {"lat": 12.2958, "lng": 76.6394}, "mysore": {"lat": 12.2958, "lng": 76.6394},
    "belagavi": {"lat": 15.8497, "lng": 74.4977}, "belgaum": {"lat": 15.8497, "lng": 74.4977},
    "bidar": {"lat": 17.9104, "lng": 77.5199}, "bider": {"lat": 17.9104, "lng": 77.5199},
    "hubballi": {"lat": 15.3647, "lng": 75.1240}, "hubli": {"lat": 15.3647, "lng": 75.1240},
    "mangaluru": {"lat": 12.9141, "lng": 74.8560}, "mangalore": {"lat": 12.9141, "lng": 74.8560},
    "shivamogga": {"lat": 13.9299, "lng": 75.5681}, "tumakuru": {"lat": 13.3392, "lng": 77.1139},

    # Maharashtra
    "mumbai": {"lat": 19.0760, "lng": 72.8777}, "pune": {"lat": 18.5204, "lng": 73.8567},
    "nagpur": {"lat": 21.1458, "lng": 79.0882}, "nashik": {"lat": 19.9975, "lng": 73.7898},
    "aurangabad": {"lat": 19.8762, "lng": 75.3433}, "solapur": {"lat": 17.6599, "lng": 75.9064},
    "kolhapur": {"lat": 16.7050, "lng": 74.2433},

    # Delhi NCR
    "delhi": {"lat": 28.7041, "lng": 77.1025}, "dehli": {"lat": 28.7041, "lng": 77.1025},
    "new delhi": {"lat": 28.6139, "lng": 77.2090}, "gurugram": {"lat": 28.4595, "lng": 77.0266},
    "gurgaon": {"lat": 28.4595, "lng": 77.0266}, "noida": {"lat": 28.5355, "lng": 77.3910},
    "faridabad": {"lat": 28.4089, "lng": 77.3178},

    # Telangana / Andhra
    "hyderabad": {"lat": 17.3850, "lng": 78.4867}, "vijayawada": {"lat": 16.5062, "lng": 80.6480},
    "visakhapatnam": {"lat": 17.6868, "lng": 83.2185}, "warangal": {"lat": 17.9784, "lng": 79.5941},
    "guntur": {"lat": 16.3067, "lng": 80.4365}, "nellore": {"lat": 14.4426, "lng": 79.9865},
    "tirupati": {"lat": 13.6288, "lng": 79.4192}, "karimnagar": {"lat": 18.4386, "lng": 79.1288},
    "rajahmundry": {"lat": 17.0005, "lng": 81.8040}, "nizamabad": {"lat": 18.6725, "lng": 78.0941},

    # Tamil Nadu
    "chennai": {"lat": 13.0827, "lng": 80.2707}, "coimbatore": {"lat": 11.0168, "lng": 76.9558},
    "madurai": {"lat": 9.9252, "lng": 78.1198}, "tiruchirappalli": {"lat": 10.7905, "lng": 78.7047},
    "trichy": {"lat": 10.7905, "lng": 78.7047}, "salem": {"lat": 11.6643, "lng": 78.1460},
    "puducherry": {"lat": 11.9416, "lng": 79.8083},

    # Gujarat
    "ahmedabad": {"lat": 23.0225, "lng": 72.5714}, "surat": {"lat": 21.1702, "lng": 72.8311},
    "vadodara": {"lat": 22.3072, "lng": 73.1812}, "rajkot": {"lat": 22.3039, "lng": 70.8022},
    "gandhinagar": {"lat": 23.2156, "lng": 72.6369},

    # Rajasthan
    "jaipur": {"lat": 26.9124, "lng": 75.7873}, "jodhpur": {"lat": 26.2389, "lng": 73.0243},
    "udaipur": {"lat": 24.5854, "lng": 73.7125}, "kota": {"lat": 25.2138, "lng": 75.8648},
    "ajmer": {"lat": 26.4499, "lng": 74.6399},

    # West Bengal / East
    "kolkata": {"lat": 22.5726, "lng": 88.3639}, "howrah": {"lat": 22.5958, "lng": 88.2636},
    "bhubaneswar": {"lat": 20.2961, "lng": 85.8245}, "patna": {"lat": 25.5941, "lng": 85.1376},
    "ranchi": {"lat": 23.3441, "lng": 85.3096}, "guwahati": {"lat": 26.1445, "lng": 91.7362},

    # Madhya Pradesh / Chhattisgarh
    "bhopal": {"lat": 23.2599, "lng": 77.4126}, "indore": {"lat": 22.7196, "lng": 75.8577},
    "raipur": {"lat": 21.2514, "lng": 81.6296}, "jabalpur": {"lat": 23.1815, "lng": 79.9864},
    "gwalior": {"lat": 26.2183, "lng": 78.1828},

    # Uttar Pradesh / Uttarakhand
    "lucknow": {"lat": 26.8467, "lng": 80.9462}, "kanpur": {"lat": 26.4499, "lng": 80.3319},
    "agra": {"lat": 27.1767, "lng": 78.0081}, "varanasi": {"lat": 25.3176, "lng": 82.9739},
    "meerut": {"lat": 28.9845, "lng": 77.7064}, "dehradun": {"lat": 30.3165, "lng": 78.0322},

    # Punjab / Haryana / Himachal / J&K
    "chandigarh": {"lat": 30.7333, "lng": 76.7794}, "ludhiana": {"lat": 30.9010, "lng": 75.8573},
    "amritsar": {"lat": 31.6340, "lng": 74.8723}, "shimla": {"lat": 31.1048, "lng": 77.1734},
    "srinagar": {"lat": 34.0837, "lng": 74.7973}, "jammu": {"lat": 32.7266, "lng": 74.8570},

    # Kerala / Goa / NE
    "kochi": {"lat": 9.9312, "lng": 76.2673}, "thiruvananthapuram": {"lat": 8.5241, "lng": 76.9366},
    "kozhikode": {"lat": 11.2588, "lng": 75.7804}, "panaji": {"lat": 15.4909, "lng": 73.8278},
    "goa": {"lat": 15.2993, "lng": 74.1240},
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