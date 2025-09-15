# Django CRUD Operations - Interview Preparation Guide

This guide provides essential CRUD (Create, Read, Update, Delete) operations code examples for Django interviews, using simplified models based on the Air Cargo Booking system.

## Table of Contents
- [Basic Model Definition](#basic-model-definition)
- [1. CREATE Operations](#1-create-operations)
- [2. READ Operations](#2-read-operations)
- [3. UPDATE Operations](#3-update-operations)
- [4. DELETE Operations](#4-delete-operations)
- [Django REST Framework CRUD](#django-rest-framework-crud)
- [Key Interview Points](#key-interview-points)

## Basic Model Definition

```python
# models.py
from django.db import models

class Booking(models.Model):
    STATUS_CHOICES = [
        ('BOOKED', 'Booked'),
        ('DEPARTED', 'Departed'),
        ('ARRIVED', 'Arrived'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    ref_id = models.CharField(max_length=20, unique=True)
    origin = models.CharField(max_length=10)
    destination = models.CharField(max_length=10)
    pieces = models.PositiveIntegerField()
    weight_kg = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='BOOKED')
    customer_name = models.CharField(max_length=100)
    customer_email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.ref_id} - {self.origin} to {self.destination}"
```

## 1. CREATE Operations

### Basic Create
```python
# Method 1: create() - creates and saves in one step
booking = Booking.objects.create(
    origin='DEL',
    destination='BOM',
    pieces=5,
    weight_kg=100,
    customer_name='John Doe',
    customer_email='john@example.com'
)

# Method 2: Manual instantiation and save()
booking = Booking(
    origin='DEL',
    destination='BOM',
    pieces=5,
    weight_kg=100,
    customer_name='John Doe',
    customer_email='john@example.com'
)
booking.save()  # Don't forget this!
```

### Create with Validation
```python
from django.core.exceptions import ValidationError

booking = Booking(
    origin='DEL',
    destination='BOM',
    pieces=0,  # Invalid - should be > 0
    weight_kg=100,
    customer_name='John Doe',
    customer_email='john@example.com'
)

try:
    booking.full_clean()  # Validates all fields
    booking.save()
except ValidationError as e:
    print(f"Validation errors: {e}")
```

### Bulk Create
```python
# Efficiently create multiple objects
bookings_data = [
    Booking(origin='DEL', destination='BOM', pieces=5, weight_kg=100, 
            customer_name='John', customer_email='john@example.com'),
    Booking(origin='BLR', destination='MAA', pieces=3, weight_kg=50,
            customer_name='Jane', customer_email='jane@example.com'),
]

created_bookings = Booking.objects.bulk_create(bookings_data)
```

## 2. READ Operations

### Basic Retrieval
```python
# Get a single object
booking = Booking.objects.get(id=1)  # Raises DoesNotExist if not found
booking = Booking.objects.get(ref_id='AC20250815C30A971C')

# Get or None (safer)
try:
    booking = Booking.objects.get(id=999)
except Booking.DoesNotExist:
    booking = None

# Or using filter().first()
booking = Booking.objects.filter(id=999).first()  # Returns None if not found

# Get all objects
all_bookings = Booking.objects.all()

# Get first/last
first_booking = Booking.objects.first()
last_booking = Booking.objects.last()
```

### Filtering
```python
# Simple filters
booked_shipments = Booking.objects.filter(status='BOOKED')
del_to_bom = Booking.objects.filter(origin='DEL', destination='BOM')

# Field lookups
recent_bookings = Booking.objects.filter(created_at__gte='2025-08-01')
heavy_bookings = Booking.objects.filter(weight_kg__gt=1000)
del_or_blr_bookings = Booking.objects.filter(origin__in=['DEL', 'BLR'])

# Complex filters with Q objects
from django.db.models import Q

complex_query = Booking.objects.filter(
    Q(origin='DEL') & Q(weight_kg__gt=500) | Q(destination='BOM')
)
```

### Ordering and Limits
```python
# Ordering
recent_first = Booking.objects.order_by('-created_at')  # Descending
by_origin = Booking.objects.order_by('origin')  # Ascending

# Slicing (LIMIT in SQL)
first_10 = Booking.objects.all()[:10]
page_2 = Booking.objects.all()[10:20]  # Pagination

# Chaining
recent_del_bookings = Booking.objects.filter(
    origin='DEL'
).order_by('-created_at')[:5]
```

### Advanced Queries
```python
from django.db.models import Count, Sum, Avg

# Annotations
bookings_with_flight_count = Booking.objects.annotate(
    flight_count=Count('flights')  # Assuming flights is a related field
)

# Aggregations
total_weight = Booking.objects.aggregate(
    total=Sum('weight_kg'),
    average=Avg('weight_kg'),
    count=Count('id')
)
```

## 3. UPDATE Operations

### Single Object Update
```python
# Method 1: Get and update
booking = Booking.objects.get(id=1)
booking.status = 'DEPARTED'
booking.save()

# Method 2: Update specific fields only
booking = Booking.objects.get(id=1)
Booking.objects.filter(id=1).update(status='DEPARTED')
```

### Bulk Updates
```python
# Update multiple objects
Booking.objects.filter(status='BOOKED').update(status='CONFIRMED')

# Update with calculations
from django.db.models import F

# Increase weight by 10% for all bookings
Booking.objects.filter(origin='DEL').update(
    weight_kg=F('weight_kg') * 1.1
)
```

### Conditional Updates
```python
# Update with conditions
updated_count = Booking.objects.filter(
    status='BOOKED',
    created_at__lt='2025-08-10'
).update(status='EXPIRED')

print(f"Updated {updated_count} bookings")
```

## 4. DELETE Operations

### Single Object Delete
```python
# Delete a specific object
booking = Booking.objects.get(id=1)
booking.delete()

# Or in one line
Booking.objects.filter(id=1).delete()
```

### Bulk Delete
```python
# Delete multiple objects
Booking.objects.filter(status='CANCELLED').delete()

# Delete with conditions
deleted_count, _ = Booking.objects.filter(
    created_at__lt='2024-01-01'
).delete()
print(f"Deleted {deleted_count} old bookings")
```

### Safe Delete Pattern
```python
# Instead of actually deleting, mark as cancelled
booking = Booking.objects.get(id=1)
if booking.status not in ['ARRIVED', 'DELIVERED']:
    booking.status = 'CANCELLED'
    booking.save()
```

## Django REST Framework CRUD

### Serializers
```python
# serializers.py
from rest_framework import serializers
from .models import Booking

class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = '__all__'
        read_only_fields = ['ref_id', 'created_at', 'updated_at']

class BookingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = [
            'origin', 'destination', 'pieces', 'weight_kg',
            'customer_name', 'customer_email'
        ]
```

### Views (Class-Based)
```python
# views.py
from rest_framework import generics
from .models import Booking
from .serializers import BookingSerializer, BookingCreateSerializer

class BookingListCreateView(generics.ListCreateAPIView):
    queryset = Booking.objects.all()
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return BookingCreateSerializer
        return BookingSerializer

class BookingDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    lookup_field = 'ref_id'
```

### Views (Function-Based with Decorators)
```python
# views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

@api_view(['GET', 'POST'])
def booking_list(request):
    if request.method == 'GET':
        bookings = Booking.objects.all()
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = BookingCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def booking_detail(request, ref_id):
    try:
        booking = Booking.objects.get(ref_id=ref_id)
    except Booking.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = BookingSerializer(booking)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = BookingSerializer(booking, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        booking.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
```

## Key Interview Points

### 1. Common Mistakes to Avoid
```python
# ❌ Wrong - forgetting to save()
booking = Booking(origin='DEL', destination='BOM')
# Missing booking.save() - object not saved to DB!

# ✅ Correct
booking = Booking(origin='DEL', destination='BOM')
booking.save()

# ❌ Inefficient - N+1 query problem
bookings = Booking.objects.all()
for booking in bookings:
    print(booking.customer.name)  # Hits DB for each booking

# ✅ Efficient - use select_related
bookings = Booking.objects.select_related('customer').all()
for booking in bookings:
    print(booking.customer.name)  # No additional DB hits
```

### 2. Performance Optimization
```python
# Use select_related for foreign keys
bookings = Booking.objects.select_related('customer').all()

# Use prefetch_related for many-to-many or reverse foreign keys
bookings = Booking.objects.prefetch_related('flights').all()

# Use only() to limit fields
bookings = Booking.objects.only('ref_id', 'origin', 'destination')

# Use defer() to exclude large fields
bookings = Booking.objects.defer('description', 'special_instructions')
```

### 3. Transaction Management
```python
from django.db import transaction

@transaction.atomic
def create_booking_with_validation(booking_data):
    try:
        booking = Booking.objects.create(**booking_data)
        # Perform additional operations
        # If any fails, everything is rolled back
        return booking
    except Exception as e:
        # Transaction automatically rolled back
        raise e
```

### 4. Error Handling Patterns
```python
# Proper exception handling
try:
    booking = Booking.objects.get(ref_id='NONEXISTENT')
except Booking.DoesNotExist:
    # Handle not found case
    return Response({'error': 'Booking not found'}, status=404)
except Booking.MultipleObjectsReturned:
    # Handle multiple objects case
    return Response({'error': 'Multiple bookings found'}, status=400)
```

This guide covers the essential CRUD operations you'll likely encounter in Django interviews. Focus on understanding the concepts rather than memorizing exact syntax.