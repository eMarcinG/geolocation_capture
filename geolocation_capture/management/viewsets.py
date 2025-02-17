from rest_framework import viewsets
from .models import Geolocation
from .serializers import GeolocationSerializer
from rest_framework.decorators import action
from rest_framework.response import Response

import os

class GeolocationViewSet(viewsets.ModelViewSet):
    queryset = Geolocation.objects.all()
    serializer_class = GeolocationSerializer

    @action(detail=False, methods=['post'])
    def fetch_geolocation(self, request):
        ip_or_url = request.data.get('ip_or_url')
        if not ip_or_url:
            return Response({"error": "IP address or URL is required"}, status=400)

        api_key = os.getenv('IPSTACK_API_KEY')
        response = requests.get(f'http://api.ipstack.com/{ip_or_url}?access_key={api_key}')
        data = response.json()

        if 'error' in data:
            return Response({"error": "Invalid IP address or URL"}, status=400)

        geolocation = Geolocation.objects.create(
            ip_address=data.get('ip'),
            url=None if 'ip' in data else ip_or_url,
            latitude=data.get('latitude'),
            longitude=data.get('longitude'),
            city=data.get('city'),
            region=data.get('region_name'),
            country=data.get('country_name')
        )

        return Response(GeolocationSerializer(geolocation).data)
