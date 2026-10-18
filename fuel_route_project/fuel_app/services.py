import os
import pandas as pd
import requests
import polyline
from dotenv import load_dotenv
from functools import lru_cache
from .constants import MAX_RANGE_MILES, VEHICLE_MPG, NEAREST_STATION_COUNT
from .utils import calculate_distance

# Load environment variables from .env file
load_dotenv()

# Retrieve OpenRouteService API key for geocoding and routing
OPENROUTE_API_KEY = os.getenv("OPENROUTE_API_KEY")

# Load fuel station data with geocoded coordinates from CSV file
fuel_df = pd.read_csv("fuel_stations_geocoded.csv")

class LocationNotFoundError(Exception):
    """Raised when a location cannot be found by the geocoding provider."""

@lru_cache(maxsize=500)
def geocode_location(location):
    """Convert a location into latitude and longitude coordinates."""
    if not OPENROUTE_API_KEY:
        raise RuntimeError("OpenRouteService API key is not configured.")

    url = "https://api.openrouteservice.org/geocode/search"

    response = requests.get(
        url,
        headers={
            "Authorization": OPENROUTE_API_KEY,
            "Content-Type": "application/json",
        },
        params={"text": location, "size": 1},
        timeout=10,
    )
    response.raise_for_status()

    data = response.json()
    features = data.get("features", [])

    if not features:
        raise LocationNotFoundError(
            f"No location found for: {location}"
        )

    coordinates = features[0]["geometry"]["coordinates"]
    return coordinates[1], coordinates[0]


def get_route(start_lat, start_lon, end_lat, end_lon):
    """
    Calculate the driving route between two points using OpenRouteService API.
    
    Args:
        start_lat (float): Starting latitude
        start_lon (float): Starting longitude
        end_lat (float): Destination latitude
        end_lon (float): Destination longitude
    
    Returns:
        dict: Route data including geometry (encoded polyline) and distance summary
    """
    # OpenRouteService directions API endpoint for car routing
    url = "https://api.openrouteservice.org/v2/directions/driving-car"

    headers = {
        "Authorization": OPENROUTE_API_KEY,
        "Content-Type": "application/json"
    }

    # Payload with start and end coordinates (GeoJSON format: [lon, lat])
    payload = {
        "coordinates": [[start_lon, start_lat], [end_lon, end_lat]]
    }

    # Request route from API
    response = requests.post(
        url,
        json=payload,
        headers=headers
    )

    # Raise exception if request failed
    response.raise_for_status()
    return response.json()

def calculate_stop_points(route_points, total_distance):
    """
    Calculate intermediate fuel stop locations along the route.
    Stops are placed at regular intervals based on vehicle fuel range.
    
    Args:
        route_points (list): List of (lat, lon) coordinates along the route
        total_distance (float): Total route distance in miles
    
    Returns:
        list: List of dicts with mile_marker and coordinate for each fuel stop
    """
    stop_points = []
    
    # Calculate how many fuel stops are needed based on vehicle range
    stop_count = int(total_distance // MAX_RANGE_MILES)

    # Generate stop points at each fuel range interval
    for i in range(1, stop_count + 1):
        # Calculate the mile marker for this stop
        mile_marker = i * MAX_RANGE_MILES

        # Calculate proportional position along the route
        ratio = mile_marker / total_distance

        # Find the closest route point to this position
        index = int(ratio * len(route_points))

        # Ensure index doesn't exceed list bounds
        index = min(index, len(route_points) - 1)

        # Store stop information
        stop_points.append({
            "mile_marker": mile_marker,
            "coordinate": route_points[index]
        })

    return stop_points

def get_best_station(stop_lat, stop_lon, used_ids):
    df = fuel_df.copy()
    df = df.dropna(subset=["Latitude", "Longitude"])

    df["distance"] = df.apply(lambda row: calculate_distance(stop_lat, stop_lon,row["Latitude"],row["Longitude"]), axis=1)

    nearby = df.nsmallest(NEAREST_STATION_COUNT,"distance")

    nearby = nearby[
        ~nearby["OPIS Truckstop ID"].isin(used_ids)]

    cheapest = nearby.loc[nearby["Retail Price"].idxmin()]
    return cheapest

def calculate_route_fuel_plan(start, finish):
    """
    Main function to calculate an optimal fuel route plan.
    
    This function:
    1. Geocodes start and finish locations
    2. Calculates the driving route
    3. Determines fuel stop points based on vehicle range
    4. Finds the cheapest fuel stations near each stop
    5. Calculates total fuel cost
    
    Args:
        start (str): Starting location (city name or address)
        finish (str): Destination location (city name or address)
    
    Returns:
        dict: Complete fuel route plan with:
            - distance_miles: Total route distance
            - fuel_required_gallons: Total fuel needed
            - fuel_stops: List of optimal refueling stops with pricing
            - total_fuel_cost: Estimated total fuel cost
    """
    # Convert location names to coordinates
    start_lat, start_lon = geocode_location(start)
    end_lat, end_lon = geocode_location(finish)

    # Get the driving route from start to finish
    route = get_route(start_lat, start_lon, end_lat, end_lon)
    route_data = route["routes"][0]
    
    # Extract distance in miles (convert from meters)
    distance_miles = route_data["summary"]["distance"] / 1609.34
    
    # Decode the polyline geometry to get individual route points
    route_points = polyline.decode(route_data["geometry"])
    
    # Calculate intermediate fuel stop locations
    stop_points = calculate_stop_points(route_points, distance_miles)

    # Find best fuel stations for each stop
    fuel_stops = []
    used_ids = set()  # Track used stations to avoid duplicates
    prices = []  # Collect prices for average calculation
    
    for stop in stop_points:
        lat, lon = stop["coordinate"]
        
        # Find the cheapest nearby station
        station = get_best_station(lat, lon, used_ids)
        used_ids.add(station["OPIS Truckstop ID"])
        prices.append(station["Retail Price"])

        # Build fuel stop information
        fuel_stops.append({
            "mile_marker": stop["mile_marker"],
            "truckstop_name": station["Truckstop Name"],
            "city": station["City"],
            "state": station["State"],
            "fuel_price": float(station["Retail Price"])
        })

    # Calculate fuel consumption and costs
    gallons = distance_miles / VEHICLE_MPG
    avg_price = sum(prices) / len(prices) if prices else 0
    total_cost = round(gallons * avg_price, 2)

    # Return complete fuel plan
    return {
        "distance_miles": round(distance_miles, 2),
        "fuel_required_gallons": round(gallons, 2),
        "fuel_stops": fuel_stops,
        "total_fuel_cost": total_cost,
    }
