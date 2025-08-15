from django.urls import path
from . import views

app_name = 'flights'

urlpatterns = [
    # Flight CRUD operations
    path('', views.FlightListCreateView.as_view(), name='flight-list-create'),
    path('<int:pk>/', views.FlightDetailView.as_view(), name='flight-detail'),
    
    # Flight search and routing
    path('search/', views.flight_search, name='flight-search'),
    path('routes/', views.get_routes, name='get-routes'),
]