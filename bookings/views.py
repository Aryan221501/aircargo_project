from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.core.cache import cache
from django.db import transaction
from .models import Booking, BookingEvent
from flights.models import Flight
from .serializers import (
    BookingSerializer, BookingCreateSerializer, BookingUpdateSerializer,
    BookingHistorySerializer, BookingEventSerializer
)
import logging
import time

logger = logging.getLogger(__name__)


class BookingListCreateView(generics.ListCreateAPIView):
    """
    List all bookings or create a new booking.
    """
    queryset = Booking.objects.all()
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return BookingCreateSerializer
        return BookingSerializer
    
    def get_queryset(self):
        queryset = Booking.objects.all()
        status_filter = self.request.query_params.get('status')
        origin = self.request.query_params.get('origin')
        destination = self.request.query_params.get('destination')
        
        if status_filter:
            queryset = queryset.filter(status__iexact=status_filter)
        if origin:
            queryset = queryset.filter(origin__iexact=origin)
        if destination:
            queryset = queryset.filter(destination__iexact=destination)
            
        return queryset.order_by('-created_at')

    def perform_create(self, serializer):
        """Create booking with distributed locking for concurrency control"""
        flight_ids = serializer.validated_data.get('flight_ids', [])
        
        # Use distributed lock for flight capacity reservation
        lock_keys = [f"flight_lock_{fid}" for fid in flight_ids]
        acquired_locks = []
        
        try:
            # Acquire locks for all flights
            for lock_key in lock_keys:
                for attempt in range(5):  # Retry up to 5 times
                    if cache.add(lock_key, "locked", timeout=30):
                        acquired_locks.append(lock_key)
                        break
                    time.sleep(0.1)  # Wait 100ms before retry
                else:
                    raise Exception(f"Could not acquire lock for {lock_key}")
            
            # Create booking within transaction
            with transaction.atomic():
                booking = serializer.save()
                logger.info(f"Created booking {booking.ref_id}")
                
        finally:
            # Release all acquired locks
            for lock_key in acquired_locks:
                cache.delete(lock_key)


class BookingDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a booking instance.
    """
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    lookup_field = 'ref_id'


@api_view(['GET'])
def booking_by_ref_id(request, ref_id):
    """
    Get booking details by reference ID.
    """
    try:
        booking = Booking.objects.get(ref_id=ref_id.upper())
        serializer = BookingSerializer(booking)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Booking.DoesNotExist:
        return Response(
            {'error': f'Booking with ref_id {ref_id} not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
def booking_history(request, ref_id):
    """
    Get booking history with full chronological event timeline.
    """
    try:
        booking = Booking.objects.get(ref_id=ref_id.upper())
        serializer = BookingHistorySerializer(booking)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Booking.DoesNotExist:
        return Response(
            {'error': f'Booking with ref_id {ref_id} not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
def depart_booking(request, ref_id):
    """
    Mark a booking as departed.
    
    Request body:
    {
        "location": "DEL",
        "flight_id": 1,  // optional
        "description": "Departed from Delhi"  // optional
    }
    """
    try:
        booking = get_object_or_404(Booking, ref_id=ref_id.upper())
        
        location = request.data.get('location', '').upper()
        flight_id = request.data.get('flight_id')
        description = request.data.get('description', '')
        
        if not location:
            return Response(
                {'error': 'Location is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        flight = None
        if flight_id:
            try:
                flight = Flight.objects.get(id=flight_id)
            except Flight.DoesNotExist:
                return Response(
                    {'error': 'Invalid flight_id'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Use distributed lock for booking updates
        lock_key = f"booking_lock_{booking.id}"
        if cache.add(lock_key, "locked", timeout=30):
            try:
                with transaction.atomic():
                    success = booking.depart(location, flight, description)
                    if success:
                        serializer = BookingSerializer(booking)
                        return Response(serializer.data, status=status.HTTP_200_OK)
                    else:
                        return Response(
                            {'error': 'Booking cannot be departed from current status'}, 
                            status=status.HTTP_400_BAD_REQUEST
                        )
            finally:
                cache.delete(lock_key)
        else:
            return Response(
                {'error': 'Booking is being updated by another process'}, 
                status=status.HTTP_409_CONFLICT
            )
            
    except Booking.DoesNotExist:
        return Response(
            {'error': f'Booking with ref_id {ref_id} not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
def arrive_booking(request, ref_id):
    """
    Mark a booking as arrived at a location.
    
    Request body:
    {
        "location": "BOM",
        "flight_id": 1,  // optional
        "description": "Arrived at Mumbai"  // optional
    }
    """
    try:
        booking = get_object_or_404(Booking, ref_id=ref_id.upper())
        
        location = request.data.get('location', '').upper()
        flight_id = request.data.get('flight_id')
        description = request.data.get('description', '')
        
        if not location:
            return Response(
                {'error': 'Location is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        flight = None
        if flight_id:
            try:
                flight = Flight.objects.get(id=flight_id)
            except Flight.DoesNotExist:
                return Response(
                    {'error': 'Invalid flight_id'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Use distributed lock for booking updates
        lock_key = f"booking_lock_{booking.id}"
        if cache.add(lock_key, "locked", timeout=30):
            try:
                with transaction.atomic():
                    success = booking.arrive(location, flight, description)
                    if success:
                        serializer = BookingSerializer(booking)
                        return Response(serializer.data, status=status.HTTP_200_OK)
                    else:
                        return Response(
                            {'error': 'Booking cannot be marked as arrived from current status'}, 
                            status=status.HTTP_400_BAD_REQUEST
                        )
            finally:
                cache.delete(lock_key)
        else:
            return Response(
                {'error': 'Booking is being updated by another process'}, 
                status=status.HTTP_409_CONFLICT
            )
            
    except Booking.DoesNotExist:
        return Response(
            {'error': f'Booking with ref_id {ref_id} not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
def deliver_booking(request, ref_id):
    """
    Mark a booking as delivered.
    
    Request body:
    {
        "description": "Delivered to customer"  // optional
    }
    """
    try:
        booking = get_object_or_404(Booking, ref_id=ref_id.upper())
        
        description = request.data.get('description', '')
        
        # Use distributed lock for booking updates
        lock_key = f"booking_lock_{booking.id}"
        if cache.add(lock_key, "locked", timeout=30):
            try:
                with transaction.atomic():
                    success = booking.deliver(description)
                    if success:
                        serializer = BookingSerializer(booking)
                        return Response(serializer.data, status=status.HTTP_200_OK)
                    else:
                        return Response(
                            {'error': 'Booking cannot be delivered from current status'}, 
                            status=status.HTTP_400_BAD_REQUEST
                        )
            finally:
                cache.delete(lock_key)
        else:
            return Response(
                {'error': 'Booking is being updated by another process'}, 
                status=status.HTTP_409_CONFLICT
            )
            
    except Booking.DoesNotExist:
        return Response(
            {'error': f'Booking with ref_id {ref_id} not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
def cancel_booking(request, ref_id):
    """
    Cancel a booking.
    """
    try:
        booking = get_object_or_404(Booking, ref_id=ref_id.upper())
        
        # Use distributed lock for booking updates
        lock_key = f"booking_lock_{booking.id}"
        if cache.add(lock_key, "locked", timeout=30):
            try:
                with transaction.atomic():
                    success = booking.cancel()
                    if success:
                        serializer = BookingSerializer(booking)
                        return Response(serializer.data, status=status.HTTP_200_OK)
                    else:
                        return Response(
                            {'error': 'Booking cannot be cancelled from current status'}, 
                            status=status.HTTP_400_BAD_REQUEST
                        )
            finally:
                cache.delete(lock_key)
        else:
            return Response(
                {'error': 'Booking is being updated by another process'}, 
                status=status.HTTP_409_CONFLICT
            )
            
    except Booking.DoesNotExist:
        return Response(
            {'error': f'Booking with ref_id {ref_id} not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
def booking_events(request, ref_id):
    """
    Get all events for a booking.
    """
    try:
        booking = Booking.objects.get(ref_id=ref_id.upper())
        events = booking.events.all().order_by('timestamp')
        serializer = BookingEventSerializer(events, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Booking.DoesNotExist:
        return Response(
            {'error': f'Booking with ref_id {ref_id} not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )