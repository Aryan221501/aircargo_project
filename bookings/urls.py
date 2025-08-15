from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    # Booking CRUD operations
    path('', views.BookingListCreateView.as_view(), name='booking-list-create'),
    path('<str:ref_id>/', views.BookingDetailView.as_view(), name='booking-detail'),
    
    # Booking search and retrieval
    path('search/<str:ref_id>/', views.booking_by_ref_id, name='booking-by-ref-id'),
    path('history/<str:ref_id>/', views.booking_history, name='booking-history'),
    path('events/<str:ref_id>/', views.booking_events, name='booking-events'),
    
    # Booking status updates
    path('depart/<str:ref_id>/', views.depart_booking, name='depart-booking'),
    path('arrive/<str:ref_id>/', views.arrive_booking, name='arrive-booking'),
    path('deliver/<str:ref_id>/', views.deliver_booking, name='deliver-booking'),
    path('cancel/<str:ref_id>/', views.cancel_booking, name='cancel-booking'),
]