from rest_framework.decorators import api_view

from rest_framework.response import Response

from .models import Alert

from .serializers import AlertSerializer


@api_view(['GET'])
def alerts_api(request):

    alerts = Alert.objects.all().order_by('-id')

    serializer = AlertSerializer(
        alerts,
        many=True
    )

    return Response(serializer.data)