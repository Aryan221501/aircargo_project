from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Q
from datetime import datetime, timedelta
from .models import Flight
from .serializers import FlightSerializer, FlightSearchSerializer, RouteSerializer
import logging

logger = logging.getLogger(__name__)


class FlightListCreateView(generics.ListCreateAPIView):
    """
    List all flights or create a new flight.
    """
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer
    
    def get_queryset(self):
        queryset = Flight.objects.all()
        origin = self.request.query_params.get('origin')
        destination = self.request.query_params.get('destination')
        date = self.request.query_params.get('date')
        
        if origin:
            queryset = queryset.filter(origin__iexact=origin)
        if destination:
            queryset = queryset.filter(destination__iexact=destination)
        if date:
            try:
                date_obj = datetime.strptime(date, '%Y-%m-%d').date()
                queryset = queryset.filter(departure_datetime__date=date_obj)
            except ValueError:
                pass
                
        return queryset.order_by('departure_datetime')


class FlightDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a flight instance.
    """
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer


@api_view(['POST'])
def get_routes(request):
    """
    Get direct flights and 1-transit routes for given origin, destination, and departure date.
    
    Request body:
    {
        "origin": "DEL",
        "destination": "BLR", 
        "departure_date": "2024-08-15"
    }
    """
    serializer = FlightSearchSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    origin = serializer.validated_data['origin']
    destination = serializer.validated_data['destination']
    departure_date = serializer.validated_data['departure_date']
    
    logger.info(f"Searching routes from {origin} to {destination} on {departure_date}")
    
    # Get direct flights
    direct_flights = Flight.objects.filter(
        origin=origin,
        destination=destination,
        departure_datetime__date=departure_date,
        available_cargo_weight__gt=0
    ).order_by('departure_datetime')
    
    # Get 1-transit routes
    transit_routes = []
    
    # Find first leg flights (origin to any intermediate destination)
    first_leg_flights = Flight.objects.filter(
        origin=origin,
        departure_datetime__date=departure_date,
        available_cargo_weight__gt=0
    ).exclude(destination=destination)
    
    for first_flight in first_leg_flights:
        # Find connecting flights from intermediate destination to final destination
        # Flight should be on same day or next day
        next_day = departure_date + timedelta(days=1)
        
        connecting_flights = Flight.objects.filter(
            origin=first_flight.destination,
            destination=destination,
            departure_datetime__date__in=[departure_date, next_day],
            departure_datetime__gt=first_flight.arrival_datetime,
            available_cargo_weight__gt=0
        ).order_by('departure_datetime')
        
        # Add valid transit routes
        for connecting_flight in connecting_flights:
            # Ensure reasonable connection time (at least 2 hours)
            connection_time = connecting_flight.departure_datetime - first_flight.arrival_datetime
            if connection_time >= timedelta(hours=2):
                transit_routes.append([first_flight, connecting_flight])
    
    # Limit transit routes to avoid too many options
    transit_routes = transit_routes[:5]
    
    response_data = {
        'direct_flights': FlightSerializer(direct_flights, many=True).data,
        'transit_routes': [
            [FlightSerializer(flight).data for flight in route] 
            for route in transit_routes
        ]
    }
    
    logger.info(f"Found {len(direct_flights)} direct flights and {len(transit_routes)} transit routes")
    
    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['GET'])
def flight_search(request):
    """
    Search flights with various filters.
    Query parameters: origin, destination, date, airline
    """
    origin = request.query_params.get('origin', '').upper()
    destination = request.query_params.get('destination', '').upper()
    date = request.query_params.get('date')
    airline = request.query_params.get('airline')
    
    queryset = Flight.objects.all()
    
    if origin:
        queryset = queryset.filter(origin=origin)
    if destination:
        queryset = queryset.filter(destination=destination)
    if date:
        try:
            date_obj = datetime.strptime(date, '%Y-%m-%d').date()
            queryset = queryset.filter(departure_datetime__date=date_obj)
        except ValueError:
            return Response(
                {'error': 'Invalid date format. Use YYYY-MM-DD'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    if airline:
        queryset = queryset.filter(airline_name__icontains=airline)
    
    # Only show flights with available cargo capacity
    queryset = queryset.filter(available_cargo_weight__gt=0)
    
    flights = queryset.order_by('departure_datetime')
    serializer = FlightSerializer(flights, many=True)
    
    return Response(serializer.data, status=status.HTTP_200_OK)