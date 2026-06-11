# Utility functions for distance calculations

from geopy.distance import geodesic


def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the geodesic distance between two geographic coordinates.
    
    Args:
        lat1 (float): Latitude of the first point
        lon1 (float): Longitude of the first point
        lat2 (float): Latitude of the second point
        lon2 (float): Longitude of the second point
    
    Returns:
        float: Distance between the two points in miles
    """
    return geodesic((lat1, lon1), (lat2, lon2)).miles