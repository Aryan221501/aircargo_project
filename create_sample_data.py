#!/usr/bin/env python3
"""
Script to create sample data for the Air Cargo Booking & Tracking System.
This will populate the database with sample flights and bookings for testing.
"""

import os
import sys
import django
from datetime import datetime, timedelta
from django.utils import timezone

# Setup Django environment
sys.path.append('/home/ubuntu/aircargo_system')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aircargo_system.settings')
django.setup()

from flights.models import Flight
from bookings.models import Booking, BookingEvent


def create_sample_flights():
    """Create sample flights for testing."""
    print("Creating sample flights...")
    
    # Define sample airports
    airports = ['DEL', 'BOM', 'BLR', 'MAA', 'CCU', 'HYD', 'AMD', 'COK']
    airlines = [
        'Air India', 'IndiGo', 'SpiceJet', 'Vistara', 'GoAir',
        'AirAsia India', 'Alliance Air', 'TruJet'
    ]
    
    flights_data = []
    flight_counter = 1000
    
    # Create flights for next 7 days
    for day_offset in range(7):
        date = timezone.now().date() + timedelta(days=day_offset)
        
        # Create flights between different airport pairs
        for i, origin in enumerate(airports):
            for j, destination in enumerate(airports):
                if origin != destination and (i + j + day_offset) % 3 == 0:  # Create selective routes
                    # Morning flight
                    departure_time = timezone.make_aware(
                        datetime.combine(date, datetime.min.time().replace(hour=8, minute=30))
                    )
                    arrival_time = departure_time + timedelta(hours=2, minutes=30)
                    
                    flight = Flight.objects.create(
                        flight_number=f"AI{flight_counter}",
                        airline_name=airlines[flight_counter % len(airlines)],
                        departure_datetime=departure_time,
                        arrival_datetime=arrival_time,
                        origin=origin,
                        destination=destination,
                        aircraft_type="Boeing 737",
                        max_cargo_weight=5000,
                        available_cargo_weight=5000
                    )
                    flights_data.append(flight)
                    flight_counter += 1
                    
                    # Evening flight
                    departure_time = timezone.make_aware(
                        datetime.combine(date, datetime.min.time().replace(hour=18, minute=45))
                    )
                    arrival_time = departure_time + timedelta(hours=2, minutes=45)
                    
                    flight = Flight.objects.create(
                        flight_number=f"6E{flight_counter}",
                        airline_name=airlines[(flight_counter + 1) % len(airlines)],
                        departure_datetime=departure_time,
                        arrival_datetime=arrival_time,
                        origin=origin,
                        destination=destination,
                        aircraft_type="Airbus A320",
                        max_cargo_weight=4500,
                        available_cargo_weight=4500
                    )
                    flights_data.append(flight)
                    flight_counter += 1
    
    print(f"Created {len(flights_data)} sample flights")
    return flights_data


def create_sample_bookings():
    """Create sample bookings for testing."""
    print("Creating sample bookings...")
    
    # Get some flights for booking
    flights = list(Flight.objects.all()[:20])
    
    if not flights:
        print("No flights available. Please create flights first.")
        return []
    
    customers = [
        {"name": "John Smith", "email": "john.smith@example.com", "phone": "+1234567890"},
        {"name": "Sarah Johnson", "email": "sarah.j@example.com", "phone": "+1234567891"},
        {"name": "Michael Brown", "email": "m.brown@example.com", "phone": "+1234567892"},
        {"name": "Emily Davis", "email": "emily.davis@example.com", "phone": "+1234567893"},
        {"name": "David Wilson", "email": "d.wilson@example.com", "phone": "+1234567894"},
        {"name": "Lisa Anderson", "email": "lisa.a@example.com", "phone": "+1234567895"},
        {"name": "Robert Taylor", "email": "r.taylor@example.com", "phone": "+1234567896"},
        {"name": "Jennifer Martinez", "email": "j.martinez@example.com", "phone": "+1234567897"},
    ]
    
    cargo_descriptions = [
        "Electronics and computer parts",
        "Pharmaceutical products",
        "Automotive spare parts",
        "Textile and garments",
        "Food and beverages",
        "Industrial machinery",
        "Books and documents",
        "Medical equipment"
    ]
    
    bookings = []
    
    for i, customer in enumerate(customers):
        flight = flights[i % len(flights)]
        
        # Create booking
        booking = Booking.objects.create(
            origin=flight.origin,
            destination=flight.destination,
            pieces=5 + (i * 2),
            weight_kg=100 + (i * 50),
            customer_name=customer["name"],
            customer_email=customer["email"],
            customer_phone=customer["phone"],
            description=cargo_descriptions[i % len(cargo_descriptions)],
            special_instructions="Handle with care" if i % 3 == 0 else ""
        )
        
        # Add flight to booking
        booking.flights.add(flight)
        
        # Reserve cargo weight
        flight.reserve_cargo_weight(booking.weight_kg)
        
        bookings.append(booking)
        
        # Create some bookings with different statuses
        if i % 4 == 1:  # 25% departed
            booking.depart(flight.origin, flight, "Cargo loaded and departed")
        elif i % 4 == 2:  # 25% arrived
            booking.depart(flight.origin, flight, "Cargo loaded and departed")
            booking.arrive(flight.destination, flight, "Cargo arrived at destination")
        elif i % 4 == 3:  # 25% delivered
            booking.depart(flight.origin, flight, "Cargo loaded and departed")
            booking.arrive(flight.destination, flight, "Cargo arrived at destination")
            booking.deliver("Cargo delivered to customer successfully")
    
    print(f"Created {len(bookings)} sample bookings")
    return bookings


def main():
    """Main function to create all sample data."""
    print("Starting sample data creation...")
    
    # Clear existing data (optional)
    print("Clearing existing data...")
    BookingEvent.objects.all().delete()
    Booking.objects.all().delete()
    Flight.objects.all().delete()
    
    # Create sample data
    flights = create_sample_flights()
    bookings = create_sample_bookings()
    
    print(f"\nSample data creation completed!")
    print(f"- Created {len(flights)} flights")
    print(f"- Created {len(bookings)} bookings")
    print(f"- Total booking events: {BookingEvent.objects.count()}")
    
    # Display some sample booking IDs
    if bookings:
        print(f"\nSample booking reference IDs:")
        for booking in bookings[:5]:
            print(f"- {booking.ref_id} ({booking.status})")


if __name__ == "__main__":
    main()
