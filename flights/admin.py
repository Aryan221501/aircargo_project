from django.contrib import admin
from .models import Flight


@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = [
        'flight_number', 'airline_name', 'origin', 'destination',
        'departure_datetime', 'arrival_datetime', 'available_cargo_weight',
        'max_cargo_weight'
    ]
    list_filter = [
        'airline_name', 'origin', 'destination', 'departure_datetime'
    ]
    search_fields = [
        'flight_number', 'airline_name', 'origin', 'destination'
    ]
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Flight Information', {
            'fields': ('flight_number', 'airline_name', 'aircraft_type')
        }),
        ('Route & Schedule', {
            'fields': ('origin', 'destination', 'departure_datetime', 'arrival_datetime')
        }),
        ('Cargo Capacity', {
            'fields': ('max_cargo_weight', 'available_cargo_weight')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).order_by('-departure_datetime')