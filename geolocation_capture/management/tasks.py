from celery import shared_task, Task
from celery.exceptions import MaxRetriesExceededError
from urllib.parse import urlparse, urlunparse
import requests
import os
import json
from .models import Geolocation
from .serializers import GeolocationSerializer
from urllib.parse import urlparse
import socket
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

def normalize_url(url):
    # Add scheme if missing
    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url
    
    parsed_url = urlparse(url)
    # Remove 'www.' prefix if present
    hostname = parsed_url.hostname.replace('www.', '') if parsed_url.hostname else None
    
    return urlunparse((parsed_url.scheme, hostname, parsed_url.path, parsed_url.params, parsed_url.query, parsed_url.fragment))

def convert_url_to_ip(url):
    try:
        url = normalize_url(url)
        parsed_url = urlparse(url)
        if not parsed_url.hostname:
            raise ValueError("Invalid URL: No hostname found")
        hostname = parsed_url.hostname
        ip_address = socket.gethostbyname(hostname)
        return ip_address
    except Exception as e:
        logger.error(f"Failed to convert URL to IP: {e}")
        return None

@shared_task(bind=True, base=CustomTask)
def fetch_and_store_geolocation(self, ip=None, url=None):
    """
    Fetches geolocation data for the given IP or URL and stores it in the Geolocation model.
    Retries up to 3 times if the request fails.

    Args:
        ip (str): The IP address to fetch geolocation data for.
        url (str): The URL to fetch geolocation data for.

    Returns:
        dict: The serialized geolocation data.
    """
    base_url = os.getenv('BASE_GEODATA_URL')
    base_api_key = os.getenv('BASE_API_KEY')
    alternative_url = os.getenv('ALTERNATIVE_GEODATA_URL')
    alternative_api_key = os.getenv('ALTERNATIVE_API_KEY')

    urls_to_try = []
    if check_url_status(base_url):
        if ip:
            urls_to_try.append(f"{base_url}/{ip}?access_key={base_api_key}")
        elif url:
            urls_to_try.append(f"{base_url}/{url}?access_key={base_api_key}")

    if check_url_status(alternative_url):
        if ip:
            urls_to_try.append(f"{alternative_url}/{ip}?token={alternative_api_key}")
        elif url:
            ip_from_url = convert_url_to_ip(url)
            if ip_from_url:
                urls_to_try.append(f"{alternative_url}/{ip_from_url}?token={alternative_api_key}")

    logger.info(f"Attempting URLs: {urls_to_try}")

    if not urls_to_try:
        raise ValueError("No correctly configured URLs in environment variables")

    last_exception = None
    data = None

    # Try each URL
    for request_url in urls_to_try:
        try:
            response = requests.get(request_url, timeout=10)
            response.raise_for_status()
            try:
                data = response.json()
                source = request_url.split('?')[0].rsplit('/', 1)[0]
                break
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON from {request_url}") from e

        except requests.RequestException as e:
            logger.error(f"Request failed: {str(e)}")
            last_exception = e

    # If all attempts failed
    if data is None:
        logger.error(f"All attempts failed for {ip or url}. Retry attempt #{self.request.retries}")
        try:
            self.retry(exc=last_exception, countdown=self.default_retry_delay)
        except MaxRetriesExceededError:
            logger.error(f"MAX RETRIES exceeded for {ip or url}")
            raise

    if 'loc' in data:
        latitude, longitude = map(float, data['loc'].split(','))
    else:
        latitude = data.get('latitude')
        longitude = data.get('longitude')

    geolocation = Geolocation.objects.create(
        ip_address=data.get('ip'),
        url=normalize_url(url) or data.get('hostname'),
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
