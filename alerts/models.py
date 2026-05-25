from django.db import models

class Alert(models.Model):

    LEVEL_CHOICES = [
        ('warning',  'Warning'),
        ('critical', 'Critical'),
    ]

    shipment_id_ref = models.CharField(max_length=100, blank=True)
    title           = models.CharField(max_length=200)
    message         = models.TextField()
    level           = models.CharField(max_length=50, choices=LEVEL_CHOICES, default='warning')
    ai_action       = models.TextField(blank=True)
    acknowledged    = models.BooleanField(default=False)
    created_at      = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title