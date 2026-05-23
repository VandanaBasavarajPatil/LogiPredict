from django.db import models

# Create your models here.
class Alert(models.Model):
    
    title = models.CharField(max_length=200)

    message = models.TextField()

    level = models.CharField(max_length=50)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):

        return self.title