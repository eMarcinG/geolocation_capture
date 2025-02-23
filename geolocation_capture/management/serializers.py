from rest_framework import serializers
from .models import Geolocation

class GeolocationSerializer(serializers.ModelSerializer):
    """
    Serializer for the Geolocation model. It serializes all fields of the model.
    """
    class Meta:
        model = Geolocation
        fields = '__all__'

