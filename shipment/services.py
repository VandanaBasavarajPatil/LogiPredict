import random

from .weather_service import get_weather
from alerts.models import Alert


def predict_delay(shipment):

    weather_data = get_weather(shipment.origin)

    weather = weather_data['weather']

    if weather in ['Rain', 'Thunderstorm', 'Fog']:

        shipment.risk_level = "High"

        shipment.status = "At Risk"

    else:

        shipment.risk_level = "Normal"

        shipment.status = "Safe"

    shipment.save()
    
def calculate_prediction_score(shipment):

    score = 45

    if shipment.risk == "High":
        score += 35

    if shipment.status == "Delayed":
        score += 15

    return min(score, 95)