"""Distances between latitude/longitude points in kilometres."""

import math


def distance_km(a_lat: float, a_lon: float, b_lat: float, b_lon: float) -> float:
    """Haversine great-circle distance; inputs in degrees, output in km."""
    for latitude, longitude in ((a_lat, a_lon), (b_lat, b_lon)):
        if not (math.isfinite(latitude) and math.isfinite(longitude)
                and -90 <= latitude <= 90 and -180 <= longitude <= 180):
            raise ValueError("Invalid latitude or longitude")
    d_lat, d_lon = math.radians(b_lat - a_lat), math.radians(b_lon - a_lon)
    value = (math.sin(d_lat / 2) ** 2 + math.cos(math.radians(a_lat))
             * math.cos(math.radians(b_lat)) * math.sin(d_lon / 2) ** 2)
    value = min(1.0, max(0.0, value))
    return 6371 * 2 * math.atan2(math.sqrt(value), math.sqrt(1 - value))
