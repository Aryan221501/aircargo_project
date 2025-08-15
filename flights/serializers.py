from rest_framework import serializers
from .models import Flight


class FlightSerializer(serializers.ModelSerializer):
    """
    Serializer for Flight model with all fields.
    """
    duration = serializers.ReadOnlyField()
    is_available_for_booking = serializers.ReadOnlyField()
    
    class Meta:
        model = Flight
        fields = [
            'id', 'flight_number', 'airline_name', 'departure_datetime',
            'arrival_datetime', 'origin', 'destination', 'aircraft_type',
            'max_cargo_weight', 'available_cargo_weight', 'created_at',
            'updated_at', 'duration', 'is_available_for_booking'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class FlightSearchSerializer(serializers.Serializer):
    """
    Serializer for flight search parameters.
    """
    origin = serializers.CharField(max_length=10)
    destination = serializers.CharField(max_length=10)
    departure_date = serializers.DateField()
    
    def validate_origin(self, value):
        return value.upper()
    
    def validate_destination(self, value):
        return value.upper()


class RouteSerializer(serializers.Serializer):
    """
    Serializer for route response containing direct and transit flights.
    """
    direct_flights = FlightSerializer(many=True, read_only=True)
    transit_routes = serializers.ListField(
        child=serializers.ListField(
            child=FlightSerializer(read_only=True)
        ),
        read_only=True
    )