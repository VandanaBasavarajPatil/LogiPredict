from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect

from .weather_service import get_weather
from .forms import ShipmentForm
from .models import Shipment
from .models import Shipment


from .services import predict_delay


def create_shipment(request):
    shipments=Shipment.objects.all()
    context={
        'shipments':shipments
    }
    return render(request, 'shipment/create_shipment.html',context)

def add_shipment(request):

    if request.method == 'POST':

        form = ShipmentForm(request.POST)

        if form.is_valid():

          shipment = form.save()

          predict_delay(shipment)

        return redirect('shipment')

    else:

        form = ShipmentForm()

    context = {
        'form': form
    }

    return render(request, 'shipment/add_shipment.html', context)

def update_shipment(request, id):

    shipment = get_object_or_404(Shipment, id=id)

    if request.method == 'POST':

        form = ShipmentForm(request.POST, instance=shipment)

        if form.is_valid():

            form.save()

            return redirect('shipment')

    else:

        form = ShipmentForm(instance=shipment)

    context = {
        'form': form
    }

    return render(request, 'shipment/add_shipment.html', context)


def delete_shipment(request, id):

    shipment = get_object_or_404(Shipment, id=id)

    shipment.delete()

    return redirect('shipment')

def test_weather(request):

    data = get_weather("Shanghai")

    print(data)

    return HttpResponse("Weather checked")



