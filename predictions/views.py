from django.shortcuts import render
from django.db.models import Avg
from shipment.models import Shipment
from shipment.services import update_shipment_telemetry, calculate_prediction_score
from django.contrib.auth.decorators import login_required

@login_required
def prediction(request):
    all_shipments = Shipment.objects.all()
    # Refresh telemetry on load
    for shipment in all_shipments:
        try:
            update_shipment_telemetry(shipment)
        except Exception as e:
            print(f"[Telemetry Warning] {e}")
    # Risk Analysis list: Medium or High/Critical risk shipments
    risky_shipments = Shipment.objects.filter(
        risk_score__gt=30
    ).order_by('-risk_score')
    for shipment in risky_shipments:
        shipment.prediction_score = calculate_prediction_score(shipment)
    # High Risk Shipments card
    high_risk_count = Shipment.objects.filter(risk_score__gte=50).count()
    # Avg Predicted Delay
    avg_score = Shipment.objects.filter(risk_score__gt=30).aggregate(avg=Avg('risk_score'))['avg'] or 0.0
    avg_delay = round((avg_score / 100.0) * 3.0, 1)
    #Model Confidence
    total = all_shipments.count()
    low_risk_on_track = all_shipments.filter(
        risk_score__lte=60
    ).exclude(status__in=['DELAYED', 'Delayed']).count()
    if total > 0:
        model_confidence = round((low_risk_on_track / total) * 100, 1)
        model_confidence = max(70.0, min(model_confidence, 99.0))
    else:
        model_confidence = 0.0
    context = {
        'shipments':           risky_shipments,
        'high_risk_shipments': high_risk_count,
        'avg_delay':           avg_delay,
        'model_confidence':    model_confidence,
        'total_shipments':     total,
    }
    return render(request, 'prediction/prediction.html', context)