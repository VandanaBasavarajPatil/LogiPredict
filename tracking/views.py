from django.shortcuts import render
from shipment.models import Shipment


def tracking(request):

    shipments = Shipment.objects.all().order_by('-id')

    context = {
        'shipments': shipments
    }

    return render(
        request,
        'tracking/tracking.html',
        context
    )