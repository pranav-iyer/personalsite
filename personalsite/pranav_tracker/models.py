from django.db import models


# Create your models here.
class Location(models.Model):
    timestamp = models.DateTimeField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    position_accuracy = models.FloatField()
    altitude = models.FloatField()
    altitude_accuracy = models.FloatField()
    heading = models.FloatField()
    speed = models.FloatField()

    class Meta:
        ordering = ["timestamp"]
