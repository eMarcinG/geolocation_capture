from django.db import models

# Create your models here.
from django.contrib.gis.db import models

class Geolocation(models.Model):
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    url = models.URLField(null=True, blank=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    city = models.CharField(max_length=255)
    region = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.ip_address or self.url} - {self.city}, {self.country}"
