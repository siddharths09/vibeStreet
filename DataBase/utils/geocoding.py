from geopy.distance import geodesic

def is_within_radius(center_coord, point_coord, radius_km=2.0):
    """Check if point is within radius of center"""
    distance = geodesic(center_coord, point_coord).kilometers
    return distance <= radius_km