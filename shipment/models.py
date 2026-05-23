from django.db import models
class Shipment(models.Model):
    shipment_id=models.CharField(max_length=100, unique=True)
    origin=models.CharField(max_length=100)
    destination=models.CharField(max_length=100)
    carrier=models.CharField(max_length=100)
    departure=models.DateTimeField()
    eta = models.DateField(null=True, blank=True)
    risk=models.CharField(max_length=50)
    status=models.CharField(max_length=50)
    created_at=models.DateTimeField(auto_now_add=True)
    on = models.CharField(max_length=200, blank=True)
    progress = models.IntegerField(default=0)

    def __str__(self):
        return self.shipment_id