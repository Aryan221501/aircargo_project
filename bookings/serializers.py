from rest_framework import serializers
from .models import Booking, BookingEvent
from flights.models import Flight
from flights.serializers import FlightSerializer


class BookingEventSerializer(serializers.ModelSerializer):
    """
    Serializer for BookingEvent model.
    """
    flight = FlightSerializer(read_only=True)
    
    class Meta:
        model = BookingEvent
        fields = [
            'id', 'event_type', 'location', 'flight', 'description',
            'timestamp', 'created_by', 'metadata'
        ]
        read_only_fields = ['id', 'timestamp']


class BookingSerializer(serializers.ModelSerializer):
    """
    Serializer for Booking model with all fields.
    """
    flights = FlightSerializer(many=True, read_only=True)
    events = BookingEventSerializer(many=True, read_only=True)
    flight_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        allow_empty=True
    )
    
    class Meta:
        model = Booking
        fields = [
            'id', 'ref_id', 'origin', 'destination', 'pieces', 'weight_kg',
            'status', 'flights', 'flight_ids', 'customer_name', 'customer_email',
            'customer_phone', 'description', 'special_instructions',
            'created_at', 'updated_at', 'current_location', 'events'
        ]
        read_only_fields = ['id', 'ref_id', 'created_at', 'updated_at', 'events']

    def validate_origin(self, value):
        return value.upper()
    
    def validate_destination(self, value):
        return value.upper()

    def validate_flight_ids(self, value):
        """Validate that all flight IDs exist"""
        if value:
            existing_flights = Flight.objects.filter(id__in=value)
            if len(existing_flights) != len(value):
                raise serializers.ValidationError("One or more flight IDs are invalid")
        return value

    def create(self, validated_data):
        flight_ids = validated_data.pop('flight_ids', [])
        booking = Booking.objects.create(**validated_data)
        
        if flight_ids:
            flights = Flight.objects.filter(id__in=flight_ids)
            booking.flights.set(flights)
            
            # Reserve cargo weight on flights and track reservations for rollback
            reserved_flights = []
            reservation_failed = False
            failure_message = ""
            
            for flight in flights:
                if flight.reserve_cargo_weight(booking.weight_kg):
                    reserved_flights.append(flight)
                else:
                    # Reservation failed
                    reservation_failed = True
                    failure_message = (
                        f"Flight {flight.flight_number} does not have sufficient cargo capacity "
                        f"({flight.available_cargo_weight}kg available, {booking.weight_kg}kg required)"
                    )
                    break
            
            # If any reservation failed, rollback all previous reservations and delete booking
            if reservation_failed:
                # Release cargo weight on previously reserved flights
                for reserved_flight in reserved_flights:
                    reserved_flight.release_cargo_weight(booking.weight_kg)
                
                # Delete the booking
                booking.delete()
                
                # Raise validation error
                raise serializers.ValidationError(failure_message)
        
        # Create initial booking event
        BookingEvent.objects.create(
            booking=booking,
            event_type='BOOKED',
            location=booking.origin,
            description=f"Booking created for {booking.pieces} pieces, {booking.weight_kg}kg"
        )
        
        return booking


class BookingCreateSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for booking creation.
    """
    flight_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True
    )
    
    class Meta:
        model = Booking
        fields = [
            'origin', 'destination', 'pieces', 'weight_kg',
            'customer_name', 'customer_email', 'customer_phone',
            'description', 'special_instructions', 'flight_ids'
        ]

    def validate_origin(self, value):
        return value.upper()
    
    def validate_destination(self, value):
        return value.upper()

    def create(self, validated_data):
        flight_ids = validated_data.pop('flight_ids', [])
        booking = Booking.objects.create(**validated_data)
        
        if flight_ids:
            flights = Flight.objects.filter(id__in=flight_ids)
            booking.flights.set(flights)
            
            # Reserve cargo weight on flights and track reservations for rollback
            reserved_flights = []
            reservation_failed = False
            failure_message = ""
            
            for flight in flights:
                if flight.reserve_cargo_weight(booking.weight_kg):
                    reserved_flights.append(flight)
                else:
                    # Reservation failed
                    reservation_failed = True
                    failure_message = (
                        f"Flight {flight.flight_number} does not have sufficient cargo capacity "
                        f"({flight.available_cargo_weight}kg available, {booking.weight_kg}kg required)"
                    )
                    break
            
            # If any reservation failed, rollback all previous reservations and delete booking
            if reservation_failed:
                # Release cargo weight on previously reserved flights
                for reserved_flight in reserved_flights:
                    reserved_flight.release_cargo_weight(booking.weight_kg)
                
                # Delete the booking
                booking.delete()
                
                # Raise validation error
                raise serializers.ValidationError(failure_message)
        
        # Create initial booking event
        BookingEvent.objects.create(
            booking=booking,
            event_type='BOOKED',
            location=booking.origin,
            description=f"Booking created for {booking.pieces} pieces, {booking.weight_kg}kg"
        )
        
        return booking


class BookingUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for booking status updates.
    """
    location = serializers.CharField(max_length=10, required=False)
    flight_id = serializers.IntegerField(required=False, allow_null=True)
    description = serializers.CharField(required=False, allow_blank=True)
    
    class Meta:
        model = Booking
        fields = ['status', 'location', 'flight_id', 'description']
        
    def validate_status(self, value):
        return value.upper()
    
    def validate_location(self, value):
        if value:
            return value.upper()
        return value


class BookingHistorySerializer(serializers.ModelSerializer):
    """
    Serializer for booking history with full timeline.
    """
    events = BookingEventSerializer(many=True, read_only=True)
    flights = FlightSerializer(many=True, read_only=True)
    
    class Meta:
        model = Booking
        fields = [
            'ref_id', 'origin', 'destination', 'pieces', 'weight_kg',
            'status', 'customer_name', 'customer_email', 'customer_phone',
            'description', 'special_instructions', 'created_at', 'updated_at',
            'current_location', 'flights', 'events'
        ]