#!/usr/bin/env python3
"""
Comprehensive test script for multiple flights capacity checking.
"""

import os
import sys
import django
from datetime import datetime, timedelta
from django.utils import timezone

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aircargo_system.settings')
django.setup()

from flights.models import Flight
from bookings.models import Booking
from bookings.serializers import BookingCreateSerializer

def test_multiple_flights_capacity_check():
    """Test booking with multiple flights where one has insufficient capacity"""
    print("Testing booking with multiple flights where one has insufficient capacity...")
    
    # Create flights
    flight1 = Flight.objects.create(
        flight_number="TEST001",
        airline_name="Test Airline",
        departure_datetime=timezone.now() + timedelta(days=1),
        arrival_datetime=timezone.now() + timedelta(days=1, hours=2),
        origin="DEL",
        destination="BOM",
        max_cargo_weight=1000,
        available_cargo_weight=1000
    )
    
    flight2 = Flight.objects.create(
        flight_number="TEST002",
        airline_name="Test Airline",
        departure_datetime=timezone.now() + timedelta(days=2),
        arrival_datetime=timezone.now() + timedelta(days=2, hours=2),
        origin="BOM",
        destination="MAA",
        max_cargo_weight=500,  # Small capacity
        available_cargo_weight=500
    )
    
    print(f"Created flight {flight1.flight_number} with capacity {flight1.max_cargo_weight}kg")
    print(f"Created flight {flight2.flight_number} with capacity {flight2.max_cargo_weight}kg")
    
    # Try to create a booking that exceeds the second flight's capacity
    booking_data = {
        "origin": "DEL",
        "destination": "MAA",
        "pieces": 10,
        "weight_kg": 750,  # Exceeds flight2 capacity but not flight1
        "customer_name": "Test Customer",
        "customer_email": "test@example.com",
        "customer_phone": "+1234567890",
        "description": "Test cargo exceeding capacity on second flight",
        "flight_ids": [flight1.id, flight2.id]  # Both flights
    }
    
    print(f"Attempting to create booking with {booking_data['weight_kg']}kg")
    print(f"This exceeds flight {flight2.flight_number}'s capacity ({flight2.available_cargo_weight}kg)")
    
    try:
        serializer = BookingCreateSerializer(data=booking_data)
        if serializer.is_valid():
            booking = serializer.save()
            print(f"ERROR: Booking was created despite exceeding capacity on flight {flight2.flight_number}")
            return False
        else:
            print(f"SUCCESS: Booking creation correctly failed with error: {serializer.errors}")
            error_message = str(serializer.errors)
            if "sufficient cargo capacity" in error_message and flight2.flight_number in error_message:
                print("SUCCESS: Error message correctly identifies the flight with capacity issue")
                # Verify that no cargo was reserved on flight1
                flight1.refresh_from_db()
                if flight1.available_cargo_weight == 1000:  # No change
                    print("SUCCESS: No cargo was reserved on other flights")
                    return True
                else:
                    print("ERROR: Cargo was incorrectly reserved on other flights")
                    return False
            else:
                print("PARTIAL: Booking creation failed but not with the expected cargo capacity error")
                return False
    except Exception as e:
        print(f"Exception occurred: {e}")
        return False
    finally:
        # Clean up
        Booking.objects.all().delete()
        Flight.objects.all().delete()

def test_multiple_flights_success():
    """Test booking with multiple flights all having sufficient capacity"""
    print("\nTesting booking with multiple flights all having sufficient capacity...")
    
    # Create flights
    flight1 = Flight.objects.create(
        flight_number="TEST003",
        airline_name="Test Airline",
        departure_datetime=timezone.now() + timedelta(days=1),
        arrival_datetime=timezone.now() + timedelta(days=1, hours=2),
        origin="DEL",
        destination="BOM",
        max_cargo_weight=1000,
        available_cargo_weight=1000
    )
    
    flight2 = Flight.objects.create(
        flight_number="TEST004",
        airline_name="Test Airline",
        departure_datetime=timezone.now() + timedelta(days=2),
        arrival_datetime=timezone.now() + timedelta(days=2, hours=2),
        origin="BOM",
        destination="MAA",
        max_cargo_weight=1000,
        available_cargo_weight=1000
    )
    
    print(f"Created flight {flight1.flight_number} with capacity {flight1.max_cargo_weight}kg")
    print(f"Created flight {flight2.flight_number} with capacity {flight2.max_cargo_weight}kg")
    
    # Create a booking within all flights' capacity
    booking_data = {
        "origin": "DEL",
        "destination": "MAA",
        "pieces": 10,
        "weight_kg": 500,  # Within all flights' capacity
        "customer_name": "Test Customer",
        "customer_email": "test@example.com",
        "customer_phone": "+1234567890",
        "description": "Test cargo within capacity on all flights",
        "flight_ids": [flight1.id, flight2.id]  # Both flights
    }
    
    print(f"Attempting to create booking with {booking_data['weight_kg']}kg")
    
    try:
        serializer = BookingCreateSerializer(data=booking_data)
        if serializer.is_valid():
            booking = serializer.save()
            print(f"SUCCESS: Booking created successfully with ref_id: {booking.ref_id}")
            
            # Check if cargo weight was reserved on both flights
            flight1.refresh_from_db()
            flight2.refresh_from_db()
            print(f"Flight {flight1.flight_number} available cargo: {flight1.available_cargo_weight}kg (expected: 500kg)")
            print(f"Flight {flight2.flight_number} available cargo: {flight2.available_cargo_weight}kg (expected: 500kg)")
            
            if flight1.available_cargo_weight == 500 and flight2.available_cargo_weight == 500:
                print("SUCCESS: Cargo weight was reserved correctly on both flights")
                return True
            else:
                print("ERROR: Cargo weight reservation issue on one or both flights")
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
    print("Starting comprehensive multiple flights capacity check tests...\n")
    
    # Run tests
    test1_result = test_multiple_flights_capacity_check()
    test2_result = test_multiple_flights_success()
    
    print("\n" + "="*60)
    print("COMPREHENSIVE MULTIPLE FLIGHTS TEST RESULTS:")
    print(f"Test 1 (insufficient capacity on one flight): {'PASS' if test1_result else 'FAIL'}")
    print(f"Test 2 (sufficient capacity on all flights): {'PASS' if test2_result else 'FAIL'}")
    
    if test1_result and test2_result:
        print("\nSUCCESS: The fix correctly handles multiple flights scenarios!")
        print("Bookings are rejected if any flight lacks sufficient capacity.")
        print("Bookings are accepted only when all flights have sufficient capacity.")
    else:
        print("\nISSUE: The fix may not be working correctly for multiple flights scenarios.")