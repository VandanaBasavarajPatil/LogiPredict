from rest_framework.decorators import api_view

from rest_framework.response import Response

from shipment.models import Shipment

from .serializers import PredictionSerializer


@api_view(['GET'])
def predictions_api(request):

    shipments = Shipment.objects.all()

    serializer = PredictionSerializer(
        shipments,
        many=True
    )

    return Response(serializer.data)