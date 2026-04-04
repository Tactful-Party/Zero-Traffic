from math import radians, sin, cos, sqrt, atan2


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    return 2 * r * atan2(sqrt(a), sqrt(1 - a))


def predict_traffic(distance_km: float) -> tuple[str, int, int]:
    if distance_km < 5:
        return 'Low', 18, 82
    if distance_km < 12:
        return 'Moderate', 28, 70
    return 'High', 42, 56
