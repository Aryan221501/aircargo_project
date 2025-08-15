from django.contrib import admin
from .models import Booking, BookingEvent


class BookingEventInline(admin.TabularInline):
    model = BookingEvent
    extra = 0
    readonly_fields = ['timestamp', 'created_by']
    fields = ['event_type', 'location', 'flight', 'description', 'timestamp', 'created_by']


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = [
        'ref_id', 'origin', 'destination', 'status', 'pieces', 'weight_kg',
        'customer_name', 'created_at'
    ]
    list_filter = [
        'status', 'origin', 'destination', 'created_at'
    ]
    search_fields = [
        'ref_id', 'customer_name', 'customer_email', 'origin', 'destination'
    ]
    readonly_fields = ['ref_id', 'created_at', 'updated_at']
    filter_horizontal = ['flights']
    inlines = [BookingEventInline]
    
    fieldsets = (
        ('Booking Information', {
            'fields': ('ref_id', 'status', 'current_location')
        }),
        ('Route & Cargo', {
            'fields': ('origin', 'destination', 'pieces', 'weight_kg', 'flights')
        }),
        ('Customer Information', {
            'fields': ('customer_name', 'customer_email', 'customer_phone')
        }),
        ('Additional Details', {
            'fields': ('description', 'special_instructions'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related().prefetch_related('flights', 'events')


@admin.register(BookingEvent)
class BookingEventAdmin(admin.ModelAdmin):
    list_display = [
        'booking', 'event_type', 'location', 'flight', 'timestamp', 'created_by'
    ]
    list_filter = [
        'event_type', 'location', 'timestamp', 'created_by'
    ]
    search_fields = [
        'booking__ref_id', 'location', 'description'
    ]
    readonly_fields = ['timestamp']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('booking', 'flight')