# predictions/views.py

from django.shortcuts import render
from django.db.models import Avg

from shipment.models import Shipment
from shipment.services import calculate_prediction_score


def prediction(request):

    # Update telemetry for all shipments to keep predictions synchronized
    from shipment.services import update_shipment_telemetry
    for shipment in Shipment.objects.all():
        try:
            update_shipment_telemetry(shipment)
        except Exception as e:
            print(f"[Telemetry Warning] {e}")

    # Fetch High and Medium risk shipments — these are shown in Risk Analysis
    shipments = Shipment.objects.filter(
        risk__in=['High', 'Medium', 'Critical']
    ).order_by('-id')

    # Attach prediction detail dict to each shipment object
    # This adds .prediction_score attribute so template can use it
    for shipment in shipments:
        shipment.prediction_score = calculate_prediction_score(shipment)

    # Count shipments where risk is High or Critical
    high_risk_shipments = Shipment.objects.filter(
        risk__in=['High', 'Critical']
    ).count()

    # Average delay: risk_score × 3 days (rough real-world estimate)
    # e.g. risk_score=0.82 → 0.82 × 3 = 2.46 days delay
    avg_score = Shipment.objects.filter(
        risk__in=['High', 'Critical', 'Medium']
    ).aggregate(avg=Avg('risk_score'))['avg'] or 0

    avg_delay = round(avg_score * 3, 1)  # Convert score → days

    context = {
        'shipments':          shipments,
        'high_risk_shipments': high_risk_shipments,
        'model_confidence':   94.2,   # Static for now — Phase 6 will make this real
        'avg_delay':          avg_delay,
    }

    return render(request, 'prediction/prediction.html', context)