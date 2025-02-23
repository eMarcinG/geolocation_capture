from django.db import models

# Create your models here.
from django.contrib.gis.db import models

class Geolocation(models.Model):
    """
    Model for storing geographical information including IP address, URL, latitude, longitude, city, region, country, timezone, and data source.
    """

    ip_address = models.GenericIPAddressField(null=True, blank=True)
    url = models.URLField(null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    postal_code = models.CharField(max_length=24, null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    region = models.CharField(max_length=255, null=True, blank=True)
    country = models.CharField(max_length=255, null=True, blank=True)
    timezone = models.CharField(max_length=120, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True,)
    source = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.ip_address or self.url} - {self.city}, {self.country}"
