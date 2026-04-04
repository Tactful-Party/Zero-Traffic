from __future__ import annotations

from ..services.prediction import haversine_km, predict_traffic


def build_routes(origin: tuple[float, float], destination: tuple[float, float], use_eco: bool = True) -> list[dict]:
    distance = haversine_km(origin[0], origin[1], destination[0], destination[1])
    traffic_level, base_minutes, eco = predict_traffic(distance)

    fastest = {
        'summary': 'Fastest route via main roads',
        'distance_km': round(distance, 1),
        'duration_min': max(8, int(distance * 2.4 + base_minutes)),
        'traffic_level': traffic_level,
        'eco_score': max(35, eco - 8),
        'warnings': ['May include heavier traffic during peak hours.'] if traffic_level != 'Low' else [],
    }
    eco_route = {
        'summary': 'Eco route with lower congestion and greener corridors',
        'distance_km': round(distance * 1.08, 1),
        'duration_min': max(10, int(distance * 2.7 + base_minutes - 5)),
        'traffic_level': 'Low' if traffic_level == 'Moderate' else traffic_level,
        'eco_score': min(95, eco + 10),
        'warnings': ['Slightly longer distance.'],
    }
    balanced = {
        'summary': 'Balanced route with stable travel time',
        'distance_km': round(distance * 1.03, 1),
        'duration_min': max(9, int(distance * 2.5 + base_minutes - 2)),
        'traffic_level': 'Moderate' if traffic_level == 'High' else traffic_level,
        'eco_score': eco,
        'warnings': [],
    }
    routes = [fastest, balanced, eco_route if use_eco else balanced]
    uniq = []
    seen = set()
    for r in routes:
        key = (r['summary'], r['distance_km'], r['duration_min'])
        if key not in seen:
            uniq.append(r)
            seen.add(key)
    return uniq
