from django.db import OperationalError
from .models import Geolocation
import socket

class GeolocationDatabaseMixin:
    def get_geolocation(self, **kwargs):
        ip = kwargs.get('ip')
        url = kwargs.get('url')

        geolocations = []

        if ip:
            geolocations = self._get_geolocations('ip_address', ip)
            if geolocations:
                return self._select_best_geolocation(geolocations)

        if url:
            geolocations = self._get_geolocations('url', url)
            if geolocations:
                return self._select_best_geolocation(geolocations)

        return None

    def _get_geolocations(self, field, value):
        try:
            return list(Geolocation.objects.using('default').filter(**{field: value}))
        except OperationalError:
            try:
                return list(Geolocation.objects.using('secondary').filter(**{field: value}))
            except OperationalError:
                return []

    def _get_hostname_from_url(self, url):
        return url.replace("http://", "").replace("https://", "").split('/')[0]

    def _select_best_geolocation(self, geolocations):
        return max(geolocations, key=lambda geo: geo.created_at)
