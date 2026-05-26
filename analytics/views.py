# analytics/views.py  — FIXED
# Changes:
#   1. delivered query matches actual STATUS_CHOICES ("Delivered" only)
#   2. delayed uses status="Delayed" not risk_score threshold
#   3. risk distribution uses correct label-based queries matching RISK_CHOICES
#   4. context now passes normal/medium/at_risk AS PERCENTAGES for the donut chart

from django.shortcuts import render
from shipment.models import Shipment
from django.db.models import Count
from shipment.services import update_shipment_telemetry
from django.contrib.auth.decorators import login_required


@login_required
def analytics_dashboard(request):

    # --- Telemetry refresh ---
    for shipment in Shipment.objects.all():
        try:
            update_shipment_telemetry(shipment)
        except Exception as e:
            print(f"[Telemetry Warning] {e}")

    total_shipments = Shipment.objects.count()

    # FIX 1: Match exact STATUS_CHOICES — "Delivered" (not "DELIVERED")
    delivered_shipments = Shipment.objects.filter(status="Delivered").count()

    # FIX 2: Delayed = status is Delayed (not a risk score threshold)
    delayed_shipments = Shipment.objects.filter(status="Delayed").count()

    # FIX 3: Risk distribution — match RISK_CHOICES labels exactly
    # Low  (0–30 risk_score, label="Low")
    # Medium (31–60, label="Medium")
    # High/Critical (61+, label="High" or "Critical")
    low_shipments      = Shipment.objects.filter(risk="Low").count()
    medium_shipments   = Shipment.objects.filter(risk="Medium").count()
    high_shipments     = Shipment.objects.filter(risk__in=["High", "Critical"]).count()
    at_risk_shipments  = high_shipments  # alias for existing template variable

    # --- Percentage calculations for donut chart ---
    if total_shipments > 0:
        low_pct    = round((low_shipments    / total_shipments) * 100)
        medium_pct = round((medium_shipments / total_shipments) * 100)
        high_pct   = 100 - low_pct - medium_pct   # ensure it adds to 100
    else:
        low_pct, medium_pct, high_pct = 0, 0, 0

    # --- Bar chart: on-time vs delayed ---
    if total_shipments > 0:
        # delivered % used for green bar
        delivered_pct  = min(int((delivered_shipments / total_shipments) * 100), 100)
        # at-risk % used for red bar
        delay_percentage = min(int((at_risk_shipments / total_shipments) * 100), 100)
    else:
        delivered_pct, delay_percentage = 0, 0

    # --- Carrier and route stats ---
    carrier_stats = (
        Shipment.objects
        .values("carrier")
        .annotate(total=Count("id"))
        .order_by("-total")
    )
    route_stats = (
        Shipment.objects
        .values("origin", "destination")
        .annotate(total=Count("id"))
        .order_by("-total")
    )

    context = {
        "total_shipments":    total_shipments,
        "delivered_shipments": delivered_shipments,
        "delayed_shipments":  delayed_shipments,
        "at_risk_shipments":  at_risk_shipments,
        "low_shipments":      low_shipments,
        "medium_shipments":   medium_shipments,
        "high_shipments":     high_shipments,
        # Percentages for charts
        "low_pct":            low_pct,
        "medium_pct":         medium_pct,
        "high_pct":           high_pct,
        "delivered_pct":      delivered_pct,
        "delay_percentage":   delay_percentage,
        # Table data
        "carrier_stats":      carrier_stats,
        "route_stats":        route_stats,
    }
    return render(request, "analytics/analytics.html", context)
