from math import radians
from math import sin
from math import cos
from math import sqrt
from math import atan2

def calculate_distance(
    lat1,
    lon1,
    lat2,
    lon2
):

    earth_radius = 6371

    dlat = radians(
        lat2 - lat1
    )

    dlon = radians(
        lon2 - lon1
    )

    a = (
        sin(dlat / 2) ** 2
        +
        cos(radians(lat1))
        *
        cos(radians(lat2))
        *
        sin(dlon / 2) ** 2
    )

    c = 2 * atan2(
        sqrt(a),
        sqrt(1 - a)
    )

    return earth_radius * c

def generate_digipin(latitude: float, longitude: float) -> str:
    # Digipin is India's National Digital Address Directory.
    # Deterministic generation mapping to alphanumeric grids in India (approx lat 8-38, lon 68-98)
    if not (8.0 <= latitude <= 38.0 and 68.0 <= longitude <= 98.0):
        # Default fallback if outside India bounds
        return "9A1B-2C3D"
        
    lat_val = int((latitude - 8.0) * 10000)
    lon_val = int((longitude - 68.0) * 10000)
    
    chars = "23456789BCDFGHJKMPQRTVWXY"
    base = len(chars)
    
    lat_str = ""
    val = lat_val
    for _ in range(4):
        lat_str += chars[val % base]
        val //= base
        
    lon_str = ""
    val = lon_val
    for _ in range(4):
        lon_str += chars[val % base]
        val //= base
        
    return f"{lat_str[:2]}{lon_str[:2]}-{lat_str[2:]}{lon_str[2:]}"