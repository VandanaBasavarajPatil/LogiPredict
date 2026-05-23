from django.shortcuts import render

from shipment.models import Shipment

from shipment.services import calculate_prediction_score


def prediction(request):

    shipments = Shipment.objects.filter(
        risk__in=['High', 'Medium']
    ).order_by('-id')[:4]

    for shipment in shipments:

        shipment.prediction_score = calculate_prediction_score(
            shipment
        )

    high_risk_shipments = Shipment.objects.filter(
        risk='High'
    ).count()

    context = {

        'shipments': shipments,

        'high_risk_shipments': high_risk_shipments,

        'model_confidence': 94.2,

        'avg_delay': 1.4,

    }

    return render(
        request,
        'prediction/prediction.html',
        context
    )