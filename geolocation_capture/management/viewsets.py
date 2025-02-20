from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Geolocation
from .serializers import GeolocationSerializer
from .tasks import fetch_and_store_geolocation

class GeolocationViewSet(viewsets.ModelViewSet):
    queryset = Geolocation.objects.all()
    serializer_class = GeolocationSerializer

    @action(detail=False, methods=['post'])
    def fetch_geolocation(self, request):
        ip = request.data.get('ip')
        if not ip:
            return Response({"error": "IP address or URL is required"}, status=400)

        result = fetch_and_store_geolocation.delay(ip)

        return Response({"status": "Task started", "task_id": result.id})
