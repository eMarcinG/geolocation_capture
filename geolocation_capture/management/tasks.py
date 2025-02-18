from celery import shared_task, Task
from celery.exceptions import MaxRetriesExceededError
import requests
import os
from .models import Geolocation
from .serializers import GeolocationSerializer

class CustomTask(Task):
    autoretry_for = (requests.RequestException,)
    max_retries = 3
    default_retry_delay = 60  # Retry after 60 seconds

@shared_task(bind=True, base=CustomTask)
def fetch_and_store_geolocation(self, ip_or_url):
    try:
        api_key = os.getenv('IPSTACK_API_KEY')
        base_url = os.getenv('BASE_GEODATA_URL')
        response = requests.get(f'{base_url}/{ip_or_url}?access_key={api_key}')
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as exc:
        # If the query to the base address failed, try the alternative address
        alternative_url = os.getenv('ALTERNATIVE_GEODATA_URL')
        try:
            response = requests.get(f'{alternative_url}?ip_or_url={ip_or_url}')
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as alt_exc:
            # Retry if problem with both of urls
            try:
                self.retry(exc=alt_exc, countdown=60)
            except MaxRetriesExceededError:
                print(f"Max retries exceeded for {ip_or_url}")
                raise
        
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
