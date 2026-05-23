from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Shipment
from .serializers import ShipmentSerializer


@api_view(['GET', 'POST'])
def shipment_api(request):

    if request.method == 'GET':

        shipments = Shipment.objects.all()

        serializer = ShipmentSerializer(
            shipments,
            many=True
        )

        return Response(serializer.data)

    elif request.method == 'POST':

        serializer = ShipmentSerializer(
            data=request.data
        )

        if serializer.is_valid():

            serializer.save()

            return Response(serializer.data)

        return Response(serializer.errors)



@api_view(['GET', 'PUT', 'DELETE'])
def shipment_detail_api(request, id):

    shipment = Shipment.objects.get(id=id)

    if request.method == 'GET':

        serializer = ShipmentSerializer(shipment)

        return Response(serializer.data)

    elif request.method == 'PUT':

        serializer = ShipmentSerializer(
            shipment,
            data=request.data
        )

        if serializer.is_valid():

            serializer.save()

            return Response(serializer.data)

        return Response(serializer.errors)

    elif request.method == 'DELETE':

        shipment.delete()

        return Response({
            'message': 'Shipment deleted successfully'
        })