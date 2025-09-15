# Air Cargo Booking & Tracking System

A comprehensive Django-based air cargo management system with a modern Bootstrap frontend, implementing all functionalities for booking, tracking, and managing air cargo shipments.

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.2.5-green)](https://www.djangoproject.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🎯 Project Overview

The Air Cargo Booking & Tracking System is a full-featured web application designed to manage the entire lifecycle of air cargo shipments. It provides a seamless interface for creating bookings, finding optimal flight routes, tracking cargo in real-time, and managing the complete shipment workflow.

### Key Features

- **Booking Management**: Create, view, and manage cargo bookings with customer details
- **Route Planning**: Intelligent flight route calculation with direct and transit options
- **Real-time Tracking**: Comprehensive tracking with detailed timeline and status updates
- **Flight Integration**: Seamless integration with flight schedules and capacity management
- **Status Management**: Complete lifecycle tracking (Booked → Departed → Arrived → Delivered)
- **Responsive UI**: Modern, mobile-friendly interface built with Bootstrap 5
- **User Authentication**: Secure user registration and login system

## 🛠 Technology Stack

### Backend
- **Django 5.2.5**: High-level Python web framework
- **Django REST Framework**: Powerful API framework
- **SQLite**: Lightweight database (easily configurable for PostgreSQL/MySQL)
- **Python 3.8+**: Programming language

### Frontend
- **Bootstrap 5**: Modern CSS framework
- **HTML5/CSS3**: Semantic markup and styling
- **JavaScript (ES6+)**: Client-side functionality
- **Axios**: Promise-based HTTP client

## 📁 Project Structure

```
aircargo_system/
├── accounts/                 # User authentication and management
│   ├── migrations/          # Database migrations for accounts
│   ├── __init__.py          # Package initializer
│   ├── admin.py             # Admin configuration
│   ├── apps.py              # App configuration
│   ├── models.py            # User models
│   ├── serializers.py       # Data serialization
│   ├── tests.py             # Unit tests
│   ├── urls.py              # Account-specific URLs
│   └── views.py             # Account API views
├── aircargo_system/          # Project settings and configuration
│   ├── __init__.py          # Package initializer
│   ├── asgi.py              # ASGI config
│   ├── settings.py          # Project settings
│   ├── urls.py              # Main URL configuration
│   └── wsgi.py              # WSGI config
├── bookings/                 # Booking management app
│   ├── migrations/          # Database migrations for bookings
│   ├── __init__.py          # Package initializer
│   ├── admin.py             # Admin configuration
│   ├── apps.py              # App configuration
│   ├── models.py            # Booking and event models
│   ├── serializers.py       # Data serialization
│   ├── tests.py             # Unit tests
│   ├── urls.py              # Booking-specific URLs
│   └── views.py             # Booking API views
├── flights/                  # Flight management app
│   ├── migrations/          # Database migrations for flights
│   ├── __init__.py          # Package initializer
│   ├── admin.py             # Admin configuration
│   ├── apps.py              # App configuration
│   ├── models.py            # Flight model
│   ├── serializers.py       # Data serialization
│   ├── tests.py             # Unit tests
│   ├── urls.py              # Flight-specific URLs
│   └── views.py             # Flight API views
├── media/                    # Media files (uploaded content)
├── static/                   # Static assets
│   └── css/                 # CSS stylesheets
│       └── clean-dark.css   # Main stylesheet
├── templates/                # HTML templates
│   ├── base.html            # Base template
│   ├── booking_detail.html  # Booking details page
│   ├── create_booking.html  # Booking creation form
│   ├── flight_integration.html # Flight integration page
│   ├── index.html           # Home page
│   └── search_booking.html  # Booking search page
├── manage.py                # Django management script
├── requirements.txt         # Python dependencies
├── create_sample_data.py    # Sample data generation script
└── sample_data.py           # Sample data definitions
```

## 📋 System Requirements

- Python 3.8+
- Django 5.2.5+
- Modern web browser
- Internet connection (for Bootstrap CDN)

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone <repository-url>
cd aircargo_system
```

### 2. Set up Virtual Environment
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Database Setup
```bash
# Apply migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser
```

### 5. Load Sample Data
```bash
python create_sample_data.py
```

### 6. Start the Development Server
```bash
python manage.py runserver
```

The application will be available at `http://127.0.0.1:8000/`

## 🌐 Application URLs

### Main Pages
- **Home**: `/` - Dashboard and overview
- **Create Booking**: `/create-booking/` - New booking form
- **Track Booking**: `/search-booking/` - Search and track bookings
- **Booking Details**: `/booking-detail/?ref_id=<ID>` - Detailed booking view
- **Admin Panel**: `/admin/` - Django admin interface

### API Endpoints
- **Flights**: `/api/flights/` - Flight management
- **Bookings**: `/api/bookings/` - Booking operations
- **Route Search**: `/api/flights/routes/` - Find available routes
- **Booking Search**: `/api/bookings/search/<ref_id>/` - Search specific booking
- **Status Updates**: `/api/bookings/{action}/<ref_id>/` - Update booking status

## 📊 Sample Data

The system includes pre-populated sample data:
- **260+ flights** across major Indian airports (DEL, BOM, BLR, MAA, CCU, HYD, AMD, COK)
- **8 sample bookings** with different statuses
- **Multiple airlines** (Air India, IndiGo, SpiceJet, Vistara, etc.)
- **Various cargo types** (Electronics, Pharmaceuticals, Automotive parts, etc.)

### Sample Booking References
- `AC20250815C30A971C` (BOOKED)
- `AC2025081506108E52` (DEPARTED)
- `AC202508157F829595` (ARRIVED)
- `AC2025081530906EA6` (DELIVERED)

## 🔧 API Usage Examples

### Create a Booking
```javascript
POST /api/bookings/
{
    "origin": "DEL",
    "destination": "BOM",
    "pieces": 5,
    "weight_kg": 100,
    "customer_name": "John Doe",
    "customer_email": "john@example.com",
    "customer_phone": "+1234567890",
    "flight_ids": [1, 2]
}
```

### Search Routes
```javascript
POST /api/flights/routes/
{
    "origin": "DEL",
    "destination": "BOM",
    "departure_date": "2025-08-16"
}
```

### Track Booking
```javascript
GET /api/bookings/search/AC20250815C30A971C/
```

### Update Booking Status
```javascript
POST /api/bookings/depart/AC20250815C30A971C/
{
    "location": "DEL",
    "description": "Cargo loaded and departed"
}
```

## 🔄 Booking Status Workflow

```
BOOKED → DEPARTED → ARRIVED → DELIVERED
   ↓         ↓         ↓         ↓
Created   Left      Reached   Customer
Booking   Origin    Destination Received
```

Status transitions are managed through the API endpoints:
- `/api/bookings/depart/<ref_id>/` - Mark as departed
- `/api/bookings/arrive/<ref_id>/` - Mark as arrived
- `/api/bookings/deliver/<ref_id>/` - Mark as delivered
- `/api/bookings/cancel/<ref_id>/` - Cancel booking (if allowed)

## 🎯 Core Functionality

### 1. Booking Management
- Create new bookings with customer and cargo details
- Automatic reference ID generation
- Flight assignment and capacity management
- Status tracking throughout the journey

### 2. Route Planning
- Direct flight search
- Transit route calculation
- Capacity availability checking
- Multi-leg journey support

### 3. Tracking System
- Real-time status updates
- Complete timeline with timestamps
- Location tracking
- Event history logging

### 4. Flight Integration
- Flight schedule management
- Cargo capacity tracking
- Automatic weight reservation
- Multi-airline support

### 5. User Authentication
- User registration and login
- Password management
- Session handling
- Access control

## 🔐 Admin Access

### Default Admin Credentials
- **Username**: admin
- **Password**: admin123
- **URL**: `/admin/`

### Admin Capabilities
- Manage flights and schedules
- View and update bookings
- Track cargo status
- Generate reports
- User management

## 📱 Responsive Design

The system features a fully responsive design that works on:
- Desktop computers
- Tablets
- Mobile phones
- Various screen sizes

Built with Bootstrap 5, the interface adapts seamlessly to different devices and screen orientations.

## 🛡 Security Features

- CSRF protection
- SQL injection prevention
- XSS protection
- Input validation
- Secure admin interface
- User authentication and session management

## 📈 Performance Features

- Optimized database queries with proper indexing
- Efficient API endpoints
- Minimal frontend dependencies
- Fast page load times
- Responsive user interface

## 🧪 Testing

### Manual Testing Completed
- Home page functionality
- Booking creation process
- Route search functionality
- Booking tracking system
- Status update workflow
- Admin interface operations
- User authentication system

### Test Files
- `test_capacity_check.py` - Flight capacity validation
- `test_capacity_check_fixed.py` - Fixed capacity validation tests
- `test_multiple_flights_capacity.py` - Multi-flight capacity tests

### Test Data Available
- Multiple booking scenarios
- Various flight routes
- Different status states
- Customer information
- Timeline tracking

## 📦 Development Guidelines

### Project Organization
The project follows Django's best practices with a modular structure:
- Each app (`accounts`, `bookings`, `flights`) contains its own models, views, and serializers
- Templates are centrally managed in the `templates/` directory
- Static assets are in the `static/` directory
- API endpoints are versioned under `/api/`

### Adding New Features
1. Create a new Django app if needed: `python manage.py startapp <app_name>`
2. Define models in `models.py`
3. Create serializers in `serializers.py`
4. Implement views in `views.py`
5. Register URLs in `urls.py`
6. Add templates as needed
7. Update this README with new features

## 🚀 Production Deployment

For production deployment, consider:
1. Using PostgreSQL/MySQL database instead of SQLite
2. Configuring proper CORS settings
3. Setting up SSL certificates
4. Using a production WSGI server (Gunicorn/uWSGI)
5. Configuring static file serving
6. Setting up monitoring and logging
7. Implementing proper backup strategies

## 📞 Support

For technical support or questions:
- Check the Django admin interface for data management
- Review API endpoints for integration
- Examine the sample data for usage examples
- Test with provided booking references

## 📄 License

This project is developed as a comprehensive air cargo management solution with all requested functionalities implemented and tested.

---

**System Status**: ✅ Fully Operational  
**Last Updated**: September 15, 2025  
**Version**: 1.0.0