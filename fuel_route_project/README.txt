# Fuel Route Optimization API

## Overview

This project is a Django REST API that calculates an optimal fuel plan for a road trip within the United States.

Given a start location and destination, the API:

* Calculates the driving route
* Determines fuel stops based on a maximum vehicle range of 500 miles
* Identifies cost-effective fuel stations
* Estimates total fuel cost assuming 10 miles per gallon
* Returns route information and fuel stop recommendations

The solution is designed with performance and minimal external API usage in mind.

---

# Features

* Latest Django and Django REST Framework
* Start and destination location support
* Route generation using OpenRouteService
* Fuel stop planning based on 500-mile vehicle range
* Fuel cost estimation
* Fuel station optimization using provided fuel price dataset
* Geocoding cache for improved performance
* Single routing API call per request
* Clean service-oriented architecture

---

# Architecture

Request Flow

Start Location
→ Geocoding
→ Route Generation
→ Fuel Stop Calculation
→ Fuel Station Optimization
→ Cost Calculation
→ API Response

The application follows a service-based architecture to keep business logic separate from API endpoints.

---

# Optimization Strategy

One of the primary goals of this project is minimizing external API calls.

Implemented optimizations:

### Route API Optimization

Only one routing API request is performed per user request.

### Geocoding Cache

Location lookups are cached using LRU Cache to avoid repeated geocoding requests for commonly searched locations.

### In-Memory Fuel Dataset

The fuel price dataset is loaded once during application startup and reused across requests.

This eliminates repeated file reads and improves response times.

---

# Fuel Stop Optimization

The vehicle is assumed to have:

* Maximum Range: 500 miles
* Fuel Efficiency: 10 MPG

Fuel stops are generated at approximately every 500 miles along the route.

For each stop point:

1. Nearby fuel stations are identified
2. Fuel prices are compared
3. The most cost-effective station is selected

This approach balances route practicality and fuel cost optimization.

---

# Dataset Note

The original assessment dataset contains:

* Truck Stop Name
* Address
* City
* State
* Fuel Price

The original dataset does not include latitude and longitude coordinates.

To demonstrate route-based optimization, a preprocessing utility (`generate_station_coordinates.py`) is included to enrich station records with geographic coordinates.

The runtime API does not perform mass geocoding and remains optimized for performance.

---

# API Endpoint

POST /api/route-fuel/

Request:

{
"start": "Dallas, TX",
"finish": "Los Angeles, CA"
}

Response:

{
"distance_miles": 1435.2,
"fuel_required_gallons": 143.52,
"fuel_stops": [...],
"total_fuel_cost": 398.10
}

---

# Technologies Used

* Python 3.12
* Django 5.2
* Django REST Framework
* Pandas
* OpenRouteService
* OpenStreetMap
* Geopy

---

# Engineering Considerations

While implementing this solution, special attention was given to:

* Reducing external API dependency
* Improving response time
* Keeping business logic modular
* Scalability for larger fuel datasets
* Clean and maintainable code structure

The design allows future enhancements such as:

* Real-time fuel prices
* Route corridor analysis
* Multi-vehicle support
* Database-backed fuel station indexing
* Advanced route optimization algorithms

---

# Author
Gayathri S. R
Backend Developer | Python | Django | REST APIs
