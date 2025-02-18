from celery import shared_task
from django.core.mail import send_mail
import requests
from .models import Geolocation
from .serializers import GeolocationSerializer
import os

@shared_task
def fetch_and_store_geolocation(ip_or_url):
    api_key = os.getenv('IPSTACK_API_KEY')
    response = requests.get(f'http://api.ipstack.com/{ip_or_url}?access_key={api_key}')
    response.raise_for_status()
    data = response.json()

    if 'error' in data:
        raise ValueError("Invalid IP address or URL")

    geolocation = Geolocation.objects.create(
        ip_address=data.get('ip'),
        url=None if 'ip' in data else ip_or_url,
        latitude=data.get('latitude'),
        longitude=data.get('longitude'),
        city=data.get('city'),
        region=data.get('region_name'),
        country=data.get('country_name')
    )

    return GeolocationSerializer(geolocation).data
