from django.db import models

class Shipment(models.Model):

    RISK_CHOICES = [
        ('Low',      'Low'),
        ('Medium',   'Medium'),
        ('High',     'High'),
        ('Critical', 'Critical'),
    ]

    STATUS_CHOICES = [
        ('Pending',    'Pending'),
        ('In Transit', 'In Transit'),
        ('At Risk',    'At Risk'),
        ('Delayed',    'Delayed'),
        ('Delivered',  'Delivered'),
    ]

    shipment_id = models.CharField(max_length=100, unique=True)
    origin      = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    carrier     = models.CharField(max_length=100)
    departure   = models.DateTimeField()
    eta         = models.DateField(null=True, blank=True)
    risk        = models.CharField(max_length=50, choices=RISK_CHOICES, default='Low')
    status      = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending')
    created_at  = models.DateTimeField(auto_now_add=True)
    on          = models.CharField(max_length=200, blank=True)
    progress    = models.IntegerField(default=0)


    risk_score          = models.FloatField(default=0.0)
    distance_km         = models.FloatField(default=0.0)
    origin_weather      = models.CharField(max_length=100, blank=True)
    origin_temp         = models.FloatField(default=0.0)
    destination_weather = models.CharField(max_length=100, blank=True)
    destination_temp    = models.FloatField(default=0.0)
    origin_lat          = models.FloatField(default=0.0)
    origin_lng          = models.FloatField(default=0.0)
    dest_lat            = models.FloatField(default=0.0)
    dest_lng            = models.FloatField(default=0.0)
    current_lat         = models.FloatField(default=0.0)
    current_lng         = models.FloatField(default=0.0)

    def __str__(self):
        return self.shipment_id