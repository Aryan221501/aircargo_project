from django.db import models
from django.core.validators import MinValueValidator
import logging

logger = logging.getLogger(__name__)


class Flight(models.Model):
    """
    Flight model representing airline flights with origin, destination, and timing information.
    """
    flight_number = models.CharField(max_length=20, unique=True, db_index=True)
    airline_name = models.CharField(max_length=100, db_index=True)
    departure_datetime = models.DateTimeField(db_index=True)
    arrival_datetime = models.DateTimeField(db_index=True)
    origin = models.CharField(max_length=10, db_index=True)  # Airport code (e.g., DEL, BOM)
    destination = models.CharField(max_length=10, db_index=True)  # Airport code
    
    # Additional fields for better functionality
    aircraft_type = models.CharField(max_length=50, blank=True, null=True)
    max_cargo_weight = models.PositiveIntegerField(
        default=10000, 
        validators=[MinValueValidator(1)],
        help_text="Maximum cargo weight in kg"
    )
    available_cargo_weight = models.PositiveIntegerField(
        default=10000, 
        validators=[MinValueValidator(0)],
        help_text="Available cargo weight in kg"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'flights'
        indexes = [
            models.Index(fields=['origin', 'destination', 'departure_datetime']),
            models.Index(fields=['departure_datetime']),
            models.Index(fields=['arrival_datetime']),
        ]
        ordering = ['departure_datetime']

    def __str__(self):
        return f"{self.flight_number} - {self.origin} to {self.destination}"

    def save(self, *args, **kwargs):
        logger.info(f"Saving flight: {self.flight_number} from {self.origin} to {self.destination}")
        super().save(*args, **kwargs)

    @property
    def duration(self):
        """Calculate flight duration"""
        return self.arrival_datetime - self.departure_datetime

    @property
    def is_available_for_booking(self):
        """Check if flight has available cargo capacity"""
        return self.available_cargo_weight > 0

    def reserve_cargo_weight(self, weight):
        """Reserve cargo weight for a booking"""
        if self.available_cargo_weight >= weight:
            self.available_cargo_weight -= weight
            self.save()
            logger.info(f"Reserved {weight}kg cargo weight on flight {self.flight_number}")
            return True
        return False

    def release_cargo_weight(self, weight):
        """Release reserved cargo weight"""
        self.available_cargo_weight = min(
            self.max_cargo_weight, 
            self.available_cargo_weight + weight
        )
        self.save()
        logger.info(f"Released {weight}kg cargo weight on flight {self.flight_number}")