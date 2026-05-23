from rest_framework import serializers

from shipment.models import Shipment


class PredictionSerializer(serializers.ModelSerializer):

    class Meta:

        model = Shipment

        fields = '__all__'