from celery import shared_task, Task
from celery.exceptions import MaxRetriesExceededError
import requests
import os
import json
from .models import Geolocation
from .serializers import GeolocationSerializer
from urllib.parse import urlparse
import logging

logger = logging.getLogger(__name__)

class CustomTask(Task):
    max_retries = 3
    default_retry_delay = 60  # Retry after 60 seconds

def check_url_status(url):
    """Checks if the URL responds with status code 200."""
    try:
        response = requests.get(url, timeout=10)  # Adding timeout for safety
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

@shared_task(bind=True, base=CustomTask)
def fetch_and_store_geolocation(self, ip):
    """
    Fetches geolocation data for the given IP and stores it in the Geolocation model.
    Retries up to 3 times if the request fails.

    Args:
        ip (str): The IP address to fetch geolocation data for.

    Returns:
        dict: The serialized geolocation data.
    """
    base_url = os.getenv('BASE_GEODATA_URL')
    base_api_key = os.getenv('BASE_API_KEY')
    alternative_url = os.getenv('ALTERNATIVE_GEODATA_URL')
    alternative_api_key = os.getenv('ALTERNATIVE_API_KEY')

    urls_to_try = []
    if check_url_status(base_url):
        urls_to_try.append(f"{base_url}/{ip}?access_key={base_api_key}")  
    if check_url_status(alternative_url):
        urls_to_try.append(f"{alternative_url}/{ip}?token={alternative_api_key}") 

    logger.info(f"Attempting URLs: {urls_to_try}")
    
    if not urls_to_try:
        raise ValueError("No correctly configured URLs in environment variables")

    last_exception = None
    data = None
    
    # Try each URL
    for url in urls_to_try:
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            try:
                data = response.json()
                source = url.split('?')[0].rsplit('/', 1)[0]
                break
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON from {url}") from e

        except requests.RequestException as e:
            logger.error(f"Request failed: {str(e)}")
            raise

    # If all attempts failed
    if data is None:
        logger.error(f"All attempts failed for {ip}. Retry attempt #{self.request.retries}")
        try:
            self.retry(exc=last_exception, countdown=self.default_retry_delay)
        except MaxRetriesExceededError:
            logger.error(f"MAX RETRIES exceeded for {ip}")
            raise

    if 'loc' in data:
        latitude, longitude = map(float, data['loc'].split(','))
    else:
        latitude = data.get('latitude')
        longitude = data.get('longitude')

    geolocation = Geolocation.objects.create(
        ip_address=data.get('ip'),
        url=None if 'ip' in data else data.get('hostname'),
        latitude=latitude,
        longitude=longitude,
        city=data.get('city'),
        region=data.get('region') or data.get('region_name'),
        country=data.get('country') or data.get('country_name'),
        postal_code=data.get('postal') or data.get('zip'),
        timezone=data.get('timezone'),
        source=source
    )
    return GeolocationSerializer(geolocation).data
