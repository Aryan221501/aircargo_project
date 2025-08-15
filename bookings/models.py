from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from flights.models import Flight
import uuid
import logging

logger = logging.getLogger(__name__)


class Booking(models.Model):
    """
    Booking model representing air cargo bookings with tracking capabilities.
    """
    
    STATUS_CHOICES = [
        ('BOOKED', 'Booked'),
        ('DEPARTED', 'Departed'),
        ('ARRIVED', 'Arrived'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    ref_id = models.CharField(
        max_length=20, 
        unique=True, 
        db_index=True,
        help_text="Human-friendly unique reference ID"
    )
    origin = models.CharField(max_length=10, db_index=True)  # Airport code
    destination = models.CharField(max_length=10, db_index=True)  # Airport code
    pieces = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    weight_kg = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='BOOKED',
        db_index=True
    )
    
    # Flight relationships (can have multiple flights for transit routes)
    flights = models.ManyToManyField(Flight, related_name='bookings', blank=True)
    
    # Customer information
    customer_name = models.CharField(max_length=100)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=20)
    
    # Additional booking details
    description = models.TextField(blank=True, null=True)
    special_instructions = models.TextField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Current location tracking
    current_location = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        db_table = 'bookings'
        indexes = [
            models.Index(fields=['ref_id']),
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['origin', 'destination']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.ref_id} - {self.origin} to {self.destination}"

    def save(self, *args, **kwargs):
        if not self.ref_id:
            self.ref_id = self.generate_ref_id()
        logger.info(f"Saving booking: {self.ref_id} with status {self.status}")
        super().save(*args, **kwargs)

    def generate_ref_id(self):
        """Generate a human-friendly reference ID"""
        timestamp = timezone.now().strftime('%Y%m%d')
        random_part = str(uuid.uuid4())[:8].upper()
        return f"AC{timestamp}{random_part}"

    def can_be_cancelled(self):
        """Check if booking can be cancelled"""
        return self.status not in ['ARRIVED', 'DELIVERED', 'CANCELLED']

    def cancel(self):
        """Cancel the booking if allowed"""
        if self.can_be_cancelled():
            old_status = self.status
            self.status = 'CANCELLED'
            self.save()
            
            # Create cancellation event
            BookingEvent.objects.create(
                booking=self,
                event_type='CANCELLED',
                location=self.current_location or self.origin,
                description=f"Booking cancelled from {old_status} status"
            )
            
            # Release reserved cargo weight on flights
            for flight in self.flights.all():
                flight.release_cargo_weight(self.weight_kg)
            
            logger.info(f"Booking {self.ref_id} cancelled")
            return True
        return False

    def depart(self, location, flight=None, description=""):
        """Mark booking as departed"""
        if self.status == 'BOOKED':
            self.status = 'DEPARTED'
            self.current_location = location
            self.save()
            
            # Create departure event
            event_desc = description or f"Departed from {location}"
            if flight:
                event_desc += f" on flight {flight.flight_number}"
            
            BookingEvent.objects.create(
                booking=self,
                event_type='DEPARTED',
                location=location,
                flight=flight,
                description=event_desc
            )
            
            logger.info(f"Booking {self.ref_id} departed from {location}")
            return True
        return False

    def arrive(self, location, flight=None, description=""):
        """Mark booking as arrived"""
        if self.status in ['DEPARTED', 'BOOKED']:
            self.status = 'ARRIVED'
            self.current_location = location
            self.save()
            
            # Create arrival event
            event_desc = description or f"Arrived at {location}"
            if flight:
                event_desc += f" on flight {flight.flight_number}"
            
            BookingEvent.objects.create(
                booking=self,
                event_type='ARRIVED',
                location=location,
                flight=flight,
                description=event_desc
            )
            
            logger.info(f"Booking {self.ref_id} arrived at {location}")
            return True
        return False

    def deliver(self, description=""):
        """Mark booking as delivered"""
        if self.status == 'ARRIVED':
            self.status = 'DELIVERED'
            self.save()
            
            # Create delivery event
            BookingEvent.objects.create(
                booking=self,
                event_type='DELIVERED',
                location=self.destination,
                description=description or f"Delivered at {self.destination}"
            )
            
            logger.info(f"Booking {self.ref_id} delivered")
            return True
        return False


class BookingEvent(models.Model):
    """
    Event tracking model for booking timeline/history.
    """
    
    EVENT_TYPES = [
        ('BOOKED', 'Booked'),
        ('DEPARTED', 'Departed'),
        ('ARRIVED', 'Arrived'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
        ('IN_TRANSIT', 'In Transit'),
        ('DELAYED', 'Delayed'),
        ('CUSTOM', 'Custom Event'),
    ]
    
    booking = models.ForeignKey(
        Booking, 
        on_delete=models.CASCADE, 
        related_name='events'
    )
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    location = models.CharField(max_length=10)  # Airport code
    flight = models.ForeignKey(
        Flight, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    
    # Additional metadata
    created_by = models.CharField(max_length=100, default='system')
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = 'booking_events'
        indexes = [
            models.Index(fields=['booking', 'timestamp']),
            models.Index(fields=['event_type', 'timestamp']),
        ]
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.booking.ref_id} - {self.event_type} at {self.location}"

    def save(self, *args, **kwargs):
        logger.info(f"Creating event: {self.event_type} for booking {self.booking.ref_id}")
        super().save(*args, **kwargs)