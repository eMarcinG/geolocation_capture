from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from .models import Geolocation
from unittest.mock import patch
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User


class GeolocationViewSetTests(APITestCase):
    databases = {'default', 'replica'}
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        
        refresh = RefreshToken.for_user(self.user)
        access_token = str(refresh.access_token)

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        
        self.url_list = reverse('geolocation-list')
        self.url_fetch = reverse('geolocation-fetch-geolocation')
        self.url_search = reverse('geolocation-search-geolocation')
        self.geolocation = Geolocation.objects.create(ip_address="8.8.8.8", url="http://example.com")
    
    def test_list_geolocations(self):
        response = self.client.get(self.url_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)
    
    @patch('management.tasks.fetch_and_store_geolocation.delay')
    def test_fetch_geolocation_task_started(self, mock_fetch_and_store_geolocation):
        mock_fetch_and_store_geolocation.return_value.id = "mock-task-id"
        
        response = self.client.post(self.url_fetch, {'ip': '8.8.8.8'}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['task_id'], "mock-task-id")
        mock_fetch_and_store_geolocation.assert_called_once_with(ip='8.8.8.8', url=None)
    
    def test_fetch_geolocation_no_data(self):
        response = self.client.post(self.url_fetch, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], "IP address or URL is required")
    
    def test_search_geolocation_found(self):
        response = self.client.get(self.url_search, {'ip': '8.8.8.8'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['ip_address'], '8.8.8.8')
    
    def test_search_geolocation_not_found(self):
        response = self.client.get(self.url_search, {'ip': '1.1.1.1'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error'], "No data found for the given IP address or URL")
    
    def test_search_geolocation_no_data(self):
        response = self.client.get(self.url_search, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], "IP address or URL is required")

if __name__ == "__main__":
    unittest.main()
