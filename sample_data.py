#!/usr/bin/env python3
"""
Script to create realistic sample data for the Air Cargo Booking & Tracking System.
This will populate the database with sample flights and bookings that showcase 
the website's functionality, including direct and transit routing options.
"""

import os
import sys
import django
from datetime import datetime, timedelta
from django.utils import timezone

# Setup Django environment
# Fix the path for Windows environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aircargo_system.settings')
django.setup()

from flights.models import Flight
from bookings.models import Booking, BookingEvent


def create_realistic_airports():
    """Define realistic airports with city names"""
    return {
        'DEL': 'Delhi',
        'BOM': 'Mumbai',
        'BLR': 'Bangalore',
        'MAA': 'Chennai',
        'CCU': 'Kolkata',
        'HYD': 'Hyderabad',
        'AMD': 'Ahmedabad',
        'COK': 'Kochi',
        'PNQ': 'Pune',
        'GOI': 'Goa',
        'JAI': 'Jaipur',
        'IXC': 'Chandigarh',
        'PAT': 'Patna',
        'BHO': 'Bhopal',
        'NAG': 'Nagpur'
    }


def create_realistic_airlines():
    """Define realistic airlines"""
    return [
        'Air India',
        'IndiGo',
        'SpiceJet',
        'Vistara',
        'GoAir',
        'AirAsia India',
        'Alliance Air',
        'TruJet'
    ]


def create_popular_routes():
    """Define popular cargo routes"""
    return [
        ('DEL', 'BOM'),  # Delhi to Mumbai
        ('DEL', 'BLR'),  # Delhi to Bangalore
        ('DEL', 'MAA'),  # Delhi to Chennai
        ('DEL', 'CCU'),  # Delhi to Kolkata
        ('DEL', 'HYD'),  # Delhi to Hyderabad
        ('BOM', 'BLR'),  # Mumbai to Bangalore
        ('BOM', 'MAA'),  # Mumbai to Chennai
        ('BOM', 'HYD'),  # Mumbai to Hyderabad
        ('BLR', 'MAA'),  # Bangalore to Chennai
        ('BLR', 'HYD'),  # Bangalore to Hyderabad
        ('MAA', 'CCU'),  # Chennai to Kolkata
        ('CCU', 'DEL'),  # Kolkata to Delhi
        ('HYD', 'DEL'),  # Hyderabad to Delhi
        ('AMD', 'DEL'),  # Ahmedabad to Delhi
        ('PNQ', 'DEL'),  # Pune to Delhi
        ('GOI', 'BOM'),  # Goa to Mumbai
        ('JAI', 'DEL'),  # Jaipur to Delhi
        ('IXC', 'DEL'),  # Chandigarh to Delhi
    ]


def create_sample_flights():
    """Create realistic sample flights for showcasing on the website"""
    print("Creating realistic sample flights...")
    
    airports = create_realistic_airports()
    airlines = create_realistic_airlines()
    popular_routes = create_popular_routes()
    
    flights_data = []
    flight_counter = 1000
    
    # Create flights for next 5 days
    for day_offset in range(5):
        date = timezone.now().date() + timedelta(days=day_offset)
        
        # Create direct flights for popular routes
        for origin, destination in popular_routes:
            # Morning flight
            departure_time = timezone.make_aware(
                datetime.combine(date, datetime.min.time().replace(hour=7, minute=0))
            )
            arrival_time = departure_time + timedelta(hours=2, minutes=30)
            
            flight_number = f"{airlines[flight_counter % len(airlines)][:2].upper()}{flight_counter}"
            flight = Flight.objects.create(
                flight_number=flight_number,
                airline_name=airlines[flight_counter % len(airlines)],
                departure_datetime=departure_time,
                arrival_datetime=arrival_time,
                origin=origin,
                destination=destination,
                aircraft_type="Boeing 737" if flight_counter % 2 == 0 else "Airbus A320",
                max_cargo_weight=5000,
                available_cargo_weight=5000
            )
            flights_data.append(flight)
            flight_counter += 1
            
            # Afternoon flight
            departure_time = timezone.make_aware(
                datetime.combine(date, datetime.min.time().replace(hour=13, minute=30))
            )
            arrival_time = departure_time + timedelta(hours=2, minutes=45)
            
            flight_number = f"{airlines[flight_counter % len(airlines)][:2].upper()}{flight_counter}"
            flight = Flight.objects.create(
                flight_number=flight_number,
                airline_name=airlines[flight_counter % len(airlines)],
                departure_datetime=departure_time,
                arrival_datetime=arrival_time,
                origin=origin,
                destination=destination,
                aircraft_type="Airbus A320" if flight_counter % 2 == 0 else "Boeing 737",
                max_cargo_weight=4500,
                available_cargo_weight=4500
            )
            flights_data.append(flight)
            flight_counter += 1
            
            # Evening flight
            departure_time = timezone.make_aware(
                datetime.combine(date, datetime.min.time().replace(hour=19, minute=0))
            )
            arrival_time = departure_time + timedelta(hours=2, minutes=30)
            
            flight_number = f"{airlines[flight_counter % len(airlines)][:2].upper()}{flight_counter}"
            flight = Flight.objects.create(
                flight_number=flight_number,
                airline_name=airlines[flight_counter % len(airlines)],
                departure_datetime=departure_time,
                arrival_datetime=arrival_time,
                origin=origin,
                destination=destination,
                aircraft_type="Boeing 777" if flight_counter % 3 == 0 else "Airbus A330",
                max_cargo_weight=10000,
                available_cargo_weight=10000
            )
            flights_data.append(flight)
            flight_counter += 1
    
    # Create some transit flights for connecting routes
    transit_routes = [
        (('DEL', 'HYD'), ('HYD', 'MAA')),  # Delhi -> Hyderabad -> Chennai
        (('DEL', 'BLR'), ('BLR', 'COK')),  # Delhi -> Bangalore -> Kochi
        (('BOM', 'PNQ'), ('PNQ', 'CCU')),  # Mumbai -> Pune -> Kolkata
        (('CCU', 'AMD'), ('AMD', 'GOI')),  # Kolkata -> Ahmedabad -> Goa
    ]
    
    for day_offset in range(3):
        date = timezone.now().date() + timedelta(days=day_offset)
        
        for (first_leg, second_leg) in transit_routes:
            # First leg
            departure_time = timezone.make_aware(
                datetime.combine(date, datetime.min.time().replace(hour=8, minute=30))
            )
            arrival_time = departure_time + timedelta(hours=2, minutes=15)
            
            flight_number = f"{airlines[flight_counter % len(airlines)][:2].upper()}{flight_counter}"
            first_flight = Flight.objects.create(
                flight_number=flight_number,
                airline_name=airlines[flight_counter % len(airlines)],
                departure_datetime=departure_time,
                arrival_datetime=arrival_time,
                origin=first_leg[0],
                destination=first_leg[1],
                aircraft_type="Boeing 737",
                max_cargo_weight=3000,
                available_cargo_weight=3000
            )
            flights_data.append(first_flight)
            flight_counter += 1
            
            # Second leg (2 hours later)
            departure_time = arrival_time + timedelta(hours=2)
            arrival_time = departure_time + timedelta(hours=2, minutes=30)
            
            flight_number = f"{airlines[flight_counter % len(airlines)][:2].upper()}{flight_counter}"
            second_flight = Flight.objects.create(
                flight_number=flight_number,
                airline_name=airlines[flight_counter % len(airlines)],
                departure_datetime=departure_time,
                arrival_datetime=arrival_time,
                origin=second_leg[0],
                destination=second_leg[1],
                aircraft_type="Airbus A320",
                max_cargo_weight=3000,
                available_cargo_weight=3000
            )
            flights_data.append(second_flight)
            flight_counter += 1
    
    print(f"Created {len(flights_data)} realistic sample flights")
    return flights_data


def create_sample_customers():
    """Create sample customers for bookings"""
    return [
        {"name": "ABC Electronics Pvt Ltd", "email": "bookings@abcelectronics.com", "phone": "+91-9876543210"},
        {"name": "Global Pharma Solutions", "email": "logistics@globalpharma.in", "phone": "+91-9876543211"},
        {"name": "Metro Fashion House", "email": "shipping@metrofashion.com", "phone": "+91-9876543212"},
        {"name": "Tech Innovations Ltd", "email": "cargo@techinnovations.in", "phone": "+91-9876543213"},
        {"name": "Fresh Produce Exports", "email": "logistics@freshproduce.in", "phone": "+91-9876543214"},
        {"name": "Industrial Machinery Corp", "email": "shipments@industrialmachinery.com", "phone": "+91-9876543215"},
        {"name": "Home Decor Imports", "email": "cargo@homedecor.in", "phone": "+91-9876543216"},
        {"name": "Automotive Parts Ltd", "email": "logistics@autoparts.in", "phone": "+91-9876543217"},
        {"name": "Medical Devices India", "email": "shipping@medicaldevices.in", "phone": "+91-9876543218"},
        {"name": "Sports Goods International", "email": "cargo@sportsinternational.com", "phone": "+91-9876543219"},
    ]


def create_sample_cargo_descriptions():
    """Create sample cargo descriptions"""
    return [
        "Electronics and computer components",
        "Pharmaceutical products and medicines",
        "Textile and garment consignment",
        "Automotive spare parts shipment",
        "Food and beverage products",
        "Industrial machinery and equipment",
        "Books and educational materials",
        "Medical equipment and devices",
        "Home decor and furniture",
        "Sports equipment and accessories",
        "Cosmetics and personal care products",
        "Agricultural products and seeds"
    ]


def create_sample_special_instructions():
    """Create sample special instructions"""
    return [
        "Handle with care - Fragile items",
        "Keep in cool storage - Temperature controlled",
        "Urgent delivery required - Express shipping",
        "Requires customs documentation",
        "Insurance coverage requested",
        "Delivery to specific address only",
        "Requires signature upon delivery",
        "Contains perishable items - Expedited shipping",
        "Hazardous materials - Special handling required",
        "Oversized cargo - Special loading equipment needed"
    ]


def create_sample_bookings():
    """Create realistic sample bookings for showcasing on the website"""
    print("Creating realistic sample bookings...")
    
    # Get flights for booking
    flights = list(Flight.objects.all())
    
    if not flights:
        print("No flights available. Please create flights first.")
        return []
    
    customers = create_sample_customers()
    cargo_descriptions = create_sample_cargo_descriptions()
    special_instructions = create_sample_special_instructions()
    
    bookings = []
    
    # Create bookings with various statuses to showcase tracking
    for i, customer in enumerate(customers):
        # Select a flight (ensure we don't go out of bounds)
        flight_index = i % len(flights)
        flight = flights[flight_index]
        
        # Create varied cargo details
        pieces = 10 + (i * 5)  # 10 to 100 pieces
        weight_kg = 200 + (i * 150)  # 200kg to 1700kg
        
        # Create booking
        booking = Booking.objects.create(
            origin=flight.origin,
            destination=flight.destination,
            pieces=pieces,
            weight_kg=weight_kg,
            customer_name=customer["name"],
            customer_email=customer["email"],
            customer_phone=customer["phone"],
            description=cargo_descriptions[i % len(cargo_descriptions)],
            special_instructions=special_instructions[i % len(special_instructions)] if i % 3 == 0 else ""
        )
        
        # Add flight to booking
        booking.flights.add(flight)
        
        # Reserve cargo weight (with our fixed capacity check)
        if flight.reserve_cargo_weight(booking.weight_kg):
            print(f"Reserved {booking.weight_kg}kg on flight {flight.flight_number} for booking {booking.ref_id}")
        else:
            print(f"Failed to reserve {booking.weight_kg}kg on flight {flight.flight_number}")
            # Delete the booking if reservation failed
            booking.delete()
            continue
        
        bookings.append(booking)
        
        # Create bookings with different statuses to showcase tracking
        if i % 5 == 1:  # 20% departed
            booking.depart(flight.origin, flight, "Cargo loaded and departed from origin")
        elif i % 5 == 2:  # 20% arrived
            booking.depart(flight.origin, flight, "Cargo loaded and departed from origin")
            booking.arrive(flight.destination, flight, "Cargo arrived at destination airport")
        elif i % 5 == 3:  # 20% delivered
            booking.depart(flight.origin, flight, "Cargo loaded and departed from origin")
            booking.arrive(flight.destination, flight, "Cargo arrived at destination airport")
            booking.deliver("Cargo delivered to consignee successfully")
        elif i % 5 == 4:  # 20% in transit (for transit routes)
            # Try to find a connecting flight for transit
            connecting_flights = Flight.objects.filter(
                origin=flight.destination
            ).exclude(destination=flight.origin)[:2]
            
            if connecting_flights:
                booking.depart(flight.origin, flight, "Cargo loaded and departed from origin")
                # Add connecting flight to booking
                for connecting_flight in connecting_flights:
                    booking.flights.add(connecting_flight)
                    if connecting_flight.reserve_cargo_weight(booking.weight_kg):
                        print(f"Reserved {booking.weight_kg}kg on connecting flight {connecting_flight.flight_number}")
                        # Create in-transit event
                        BookingEvent.objects.create(
                            booking=booking,
                            event_type='IN_TRANSIT',
                            location=flight.destination,
                            flight=connecting_flight,
                            description=f"Cargo in transit to {connecting_flight.destination} on flight {connecting_flight.flight_number}"
                        )
                        break
                    else:
                        print(f"Failed to reserve {booking.weight_kg}kg on connecting flight {connecting_flight.flight_number}")
    
    # Create some bookings with transit routes
    transit_flights = Flight.objects.filter(
        origin__in=['DEL', 'BOM', 'CCU']
    ).filter(
        destination__in=['HYD', 'BLR', 'PNQ']
    )[:5]
    
    for i, flight in enumerate(transit_flights):
        if i < len(customers):
            customer = customers[i]
            pieces = 15 + (i * 3)
            weight_kg = 300 + (i * 100)
            
            booking = Booking.objects.create(
                origin=flight.origin,
                destination='MAA' if flight.destination == 'HYD' else 'COK' if flight.destination == 'BLR' else 'GOI',
                pieces=pieces,
                weight_kg=weight_kg,
                customer_name=customer["name"],
                customer_email=customer["email"],
                customer_phone=customer["phone"],
                description=cargo_descriptions[(i + 5) % len(cargo_descriptions)],
                special_instructions=special_instructions[(i + 3) % len(special_instructions)] if i % 2 == 0 else ""
            )
            
            # Add first leg flight
            booking.flights.add(flight)
            
            # Reserve cargo weight on first flight
            if flight.reserve_cargo_weight(booking.weight_kg):
                print(f"Reserved {booking.weight_kg}kg on transit flight {flight.flight_number}")
                
                # Find connecting flight
                connecting_flight = Flight.objects.filter(
                    origin=flight.destination,
                    destination=booking.destination
                ).first()
                
                if connecting_flight:
                    booking.flights.add(connecting_flight)
                    if connecting_flight.reserve_cargo_weight(booking.weight_kg):
                        print(f"Reserved {booking.weight_kg}kg on connecting flight {connecting_flight.flight_number}")
                        
                        # Mark as departed on first flight
                        booking.depart(flight.origin, flight, "Cargo loaded and departed from origin")
                        
                        # Create in-transit event
                        BookingEvent.objects.create(
                            booking=booking,
                            event_type='IN_TRANSIT',
                            location=flight.destination,
                            flight=connecting_flight,
                            description=f"Cargo in transit to {connecting_flight.destination} on flight {connecting_flight.flight_number}"
                        )
                        
                        bookings.append(booking)
                    else:
                        print(f"Failed to reserve {booking.weight_kg}kg on connecting flight {connecting_flight.flight_number}")
                        booking.delete()
                else:
                    bookings.append(booking)
            else:
                print(f"Failed to reserve {booking.weight_kg}kg on transit flight {flight.flight_number}")
                booking.delete()
    
    print(f"Created {len(bookings)} realistic sample bookings")
    return bookings


def display_sample_data_info(flights, bookings):
    """Display information about the created sample data"""
    print("\n" + "="*60)
    print("SAMPLE DATA CREATION COMPLETED SUCCESSFULLY!")
    print("="*60)
    print(f"Total flights created: {len(flights)}")
    print(f"Total bookings created: {len(bookings)}")
    print(f"Total booking events: {BookingEvent.objects.count()}")
    
    # Show booking statistics
    booked_count = len([b for b in bookings if b.status == 'BOOKED'])
    departed_count = len([b for b in bookings if b.status == 'DEPARTED'])
    arrived_count = len([b for b in bookings if b.status == 'ARRIVED'])
    delivered_count = len([b for b in bookings if b.status == 'DELIVERED'])
    
    print(f"\nBooking Status Distribution:")
    print(f"  - Booked: {booked_count}")
    print(f"  - Departed: {departed_count}")
    print(f"  - Arrived: {arrived_count}")
    print(f"  - Delivered: {delivered_count}")
    
    # Display some sample booking IDs for testing
    if bookings:
        print(f"\nSample Booking Reference IDs for Testing:")
        for booking in bookings[:10]:
            print(f"  - {booking.ref_id} ({booking.status}) - {booking.origin} to {booking.destination}")
    
    # Show popular routes
    print(f"\nPopular Routes Available:")
    routes = {}
    for flight in flights:
        route = f"{flight.origin} to {flight.destination}"
        routes[route] = routes.get(route, 0) + 1
    
    sorted_routes = sorted(routes.items(), key=lambda x: x[1], reverse=True)
    for route, count in sorted_routes[:10]:
        print(f"  - {route} ({count} flights)")


def main():
    """Main function to create all realistic sample data"""
    print("Starting realistic sample data creation...")
    print("This will populate the database with data that showcases the website's functionality.")
    
    # Clear existing data (optional)
    print("\nClearing existing data...")
    BookingEvent.objects.all().delete()
    Booking.objects.all().delete()
    Flight.objects.all().delete()
    
    # Create realistic sample data
    flights = create_sample_flights()
    bookings = create_sample_bookings()
    
    # Display information about created data
    display_sample_data_info(flights, bookings)
    
    print(f"\nReady to showcase the website with realistic sample data!")
    print("You can now run the server and view the flights and bookings on the website.")


if __name__ == "__main__":
    main()