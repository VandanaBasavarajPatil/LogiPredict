from django.shortcuts import render
from shipment.models import Shipment
from alerts.models import Alert

import requests


def dashboard(request):

    shipments = Shipment.objects.all()

    alerts = Alert.objects.all().order_by('-id')[:3]

    total_shipments = shipments.count()

    at_risk_shipments = 0

    delivered_today = Shipment.objects.filter(
        status="Delivered"
    ).count()


    # WEATHER + AI RISK CHECK
    for shipment in shipments:

        try:

            city = shipment.origin

            api_key = "YOUR_API_KEY"

            url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"

            response = requests.get(url)

            data = response.json()

            weather_condition = data['weather'][0]['main']


            # AI RISK LOGIC
            if weather_condition in ["Rain", "Thunderstorm", "Snow"]:

                shipment.status = "At Risk"

                shipment.save()

                at_risk_shipments += 1

            else:

                shipment.status = "In Transit"

                shipment.save()


        except Exception as e:

            print("Weather Error:", e)



    # RECENT SHIPMENTS
    recent_shipments = Shipment.objects.all().order_by('-id')[:5]



    # AVG RISK SCORE
    if total_shipments > 0:

        avg_risk_score = int(
            (at_risk_shipments / total_shipments) * 100
        )

    else:

        avg_risk_score = 0



    context = {

        'total_shipments': total_shipments,

        'at_risk_shipments': at_risk_shipments,

        'delivered_today': delivered_today,

        'recent_shipments': recent_shipments,

        'alerts': alerts,

        'avg_risk_score': avg_risk_score,

    }

    return render(
        request,
        'dashboard.html',
        context
    )