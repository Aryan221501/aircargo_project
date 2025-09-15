#!/usr/bin/env python3
"""
Test script to check if the system properly handles bookings larger than cargo capacity after the fix.
"""

import os
import sys
import django
from datetime import datetime, timedelta
from django.utils import timezone
from django.core.exceptions import ValidationError
from rest_framework.serializers import ValidationError as SerializerValidationError

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aircargo_system.settings')
django.setup()

from flights.models import Flight
from bookings.models import Booking
from bookings.serializers import BookingCreateSerializer

def test_booking_larger_than_capacity():
    """Test creating a booking larger than flight capacity"""
    print("Testing booking larger than flight capacity...")
    
    # Create a flight with limited cargo capacity
    flight = Flight.objects.create(
        flight_number="TEST001",
        airline_name="Test Airline",
        departure_datetime=timezone.now() + timedelta(days=1),
        arrival_datetime=timezone.now() + timedelta(days=1, hours=2),
        origin="DEL",
        destination="BOM",
        max_cargo_weight=1000,  # 1000 kg max
        available_cargo_weight=1000  # 1000 kg available
    )
    
    print(f"Created flight {flight.flight_number} with max capacity {flight.max_cargo_weight}kg")
    
    # Try to create a booking that exceeds the flight capacity
    booking_data = {
        "origin": "DEL",
        "destination": "BOM",
        "pieces": 10,
        "weight_kg": 1500,  # 1500kg - exceeds capacity
        "customer_name": "Test Customer",
        "customer_email": "test@example.com",
        "customer_phone": "+1234567890",
        "description": "Test cargo exceeding capacity",
        "flight_ids": [flight.id]
    }
    
    print(f"Attempting to create booking with {booking_data['weight_kg']}kg (exceeds capacity)")
    
    try:
        serializer = BookingCreateSerializer(data=booking_data)
        if serializer.is_valid():
            booking = serializer.save()
            print(f"ERROR: Booking was created despite exceeding capacity: {booking.ref_id}")
            return False
        else:
            print(f"SUCCESS: Booking creation correctly failed with error: {serializer.errors}")
            # Check if the error is related to cargo capacity
            error_message = str(serializer.errors)
            if "sufficient cargo capacity" in error_message:
                print("SUCCESS: Error message correctly indicates cargo capacity issue")
                return True
            else:
                print("PARTIAL: Booking creation failed but not with the expected cargo capacity error")
                return False
    except SerializerValidationError as e:
        print(f"SUCCESS: Serializer validation error caught: {e}")
        error_message = str(e)
        if "sufficient cargo capacity" in error_message:
            print("SUCCESS: Error message correctly indicates cargo capacity issue")
            return True
        else:
            print("PARTIAL: Validation error caught but not with the expected cargo capacity message")
            return False
    except Exception as e:
        print(f"Unexpected exception occurred: {e}")
        return False
    finally:
        # Clean up
        Booking.objects.all().delete()
        Flight.objects.all().delete()

def test_booking_within_capacity():
    """Test creating a booking within flight capacity"""
    print("\nTesting booking within flight capacity...")
    
    # Create a flight with sufficient cargo capacity
    flight = Flight.objects.create(
        flight_number="TEST002",
        airline_name="Test Airline",
        departure_datetime=timezone.now() + timedelta(days=1),
        arrival_datetime=timezone.now() + timedelta(days=1, hours=2),
        origin="DEL",
        destination="BOM",
        max_cargo_weight=2000,  # 2000 kg max
        available_cargo_weight=2000  # 2000 kg available
    )
    
    print(f"Created flight {flight.flight_number} with max capacity {flight.max_cargo_weight}kg")
    
    # Create a booking within the flight capacity
    booking_data = {
        "origin": "DEL",
        "destination": "BOM",
        "pieces": 5,
        "weight_kg": 500,  # 500kg - within capacity
        "customer_name": "Test Customer",
        "customer_email": "test@example.com",
        "customer_phone": "+1234567890",
        "description": "Test cargo within capacity",
        "flight_ids": [flight.id]
    }
    
    print(f"Attempting to create booking with {booking_data['weight_kg']}kg (within capacity)")
    
    try:
        serializer = BookingCreateSerializer(data=booking_data)
        if serializer.is_valid():
            booking = serializer.save()
            print(f"SUCCESS: Booking created successfully with ref_id: {booking.ref_id}")
            
            # Check if cargo weight was reserved on the flight
            flight.refresh_from_db()
            print(f"Flight available cargo after booking: {flight.available_cargo_weight}kg")
            print(f"Expected available cargo: {2000 - 500}kg")
            
            if flight.available_cargo_weight == 1500:  # 2000 - 500
                print("SUCCESS: Cargo weight was reserved correctly")
                return True
            else:
                print("ERROR: Cargo weight reservation issue")
                return False
        else:
            print(f"ERROR: Serializer validation failed: {serializer.errors}")
            return False
    except Exception as e:
        print(f"Exception occurred: {e}")
        return False
    finally:
        # Clean up
        Booking.objects.all().delete()
        Flight.objects.all().delete()

if __name__ == "__main__":
    print("Starting capacity check tests after fix...\n")
    
    # Run tests
    test1_result = test_booking_larger_than_capacity()
    test2_result = test_booking_within_capacity()
    
    print("\n" + "="*50)
    print("TEST RESULTS AFTER FIX:")
    print(f"Test 1 (exceeding capacity): {'PASS' if test1_result else 'FAIL'}")
    print(f"Test 2 (within capacity): {'PASS' if test2_result else 'FAIL'}")
    
    if test1_result and test2_result:
        print("\nSUCCESS: The fix correctly prevents bookings that exceed flight capacity!")
        print("Bookings within capacity are still processed correctly.")
    else:
        print("\nISSUE: The fix may not be working as expected.")