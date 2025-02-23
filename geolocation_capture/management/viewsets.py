# Django imports
from django.shortcuts import get_object_or_404

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Geolocation
from .serializers import GeolocationSerializer
from .tasks import fetch_and_store_geolocation
from .mixins import GeolocationDatabaseMixin
from .permissions import IsAdminOrReadOnly



class GeolocationViewSet(viewsets.ModelViewSet, GeolocationDatabaseMixin):
    """
    A viewset for viewing and editing geolocation instances.
    """
    queryset = Geolocation.objects.all()
    serializer_class = GeolocationSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['ip_address', 'url']
    search_fields = ['ip_address', 'url']

    @action(detail=False, methods=['post'], url_path='fetch', permission_classes=[IsAuthenticated])
    def fetch_geolocation(self, request):
        """
        A custom action to fetch geolocation data for a given IP address and store it.
        """
        ip = request.data.get('ip')
        if not ip:
            return Response({"error": "IP address or URL is required"}, status=400)

        result = fetch_and_store_geolocation.delay(ip)

        return Response({"status": "Task started", "task_id": result.id})

    @action(detail=False, methods=['get'], url_path='search', permission_classes=[IsAuthenticated])
    def search_geolocation(self, request):
        """
        A custom action to search geolocation data for a given IP address or URL.
        """
        ip = request.query_params.get('ip')
        url = request.query_params.get('url')

        if not ip and not url:
            return Response({"error": "IP address or URL is required"}, status=400)

        geolocation = self.get_geolocation(ip=ip, url=url)

        if not geolocation:
            return Response({"error": "No data found for the given IP address or URL"}, status=404)

        serializer = GeolocationSerializer(geolocation)
        return Response(serializer.data)
