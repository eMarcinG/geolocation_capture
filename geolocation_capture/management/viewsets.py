from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Geolocation
from .serializers import GeolocationSerializer
from .tasks import fetch_and_store_geolocation

class GeolocationViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing geolocation instances.
    """
    queryset = Geolocation.objects.all()
    serializer_class = GeolocationSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'])
    def fetch_geolocation(self, request):
        """
        A custom action to fetch geolocation data for a given IP address and store it.
        """
        ip = request.data.get('ip')
        if not ip:
            return Response({"error": "IP address or URL is required"}, status=400)

        result = fetch_and_store_geolocation.delay(ip)

        return Response({"status": "Task started", "task_id": result.id})
