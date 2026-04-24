import math
from datetime import datetime

# Approximate coordinates for common Metro Manila areas
MANILA_AREAS: dict[str, tuple[float, float]] = {
    "Makati CBD": (14.5547, 121.0244),
    "BGC Taguig": (14.5465, 121.0507),
    "Ortigas Pasig": (14.5873, 121.0615),
    "Quezon City (Commonwealth)": (14.6960, 121.0583),
    "Mandaluyong": (14.5794, 121.0359),
    "Pasay": (14.5378, 120.9982),
    "Paranaque": (14.4793, 121.0198),
    "Manila (Ermita)": (14.5890, 120.9800),
    "Marikina": (14.6507, 121.1029),
    "Las Pinas": (14.4478, 120.9936),
    "Alabang Muntinlupa": (14.4148, 121.0413),
    "Cubao QC": (14.6189, 121.0524),
}

# Road distance is typically 1.3–1.5x haversine; use 1.4 as Manila road factor
ROAD_FACTOR = 1.4


def haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlng / 2) ** 2
    return R * 2 * math.asin(math.sqrt(a))


def road_distance_km(origin: str, destination: str) -> float:
    """MOCK: straight-line * road factor. Replace with Directions API."""
    coords1 = MANILA_AREAS.get(origin)
    coords2 = MANILA_AREAS.get(destination)
    if not coords1 or not coords2:
        return 10.0  # MOCK_DEFAULT if area not in registry
    straight = haversine_km(*coords1, *coords2)
    return round(straight * ROAD_FACTOR, 2)


def traffic_factor(departure_dt: datetime) -> float:
    """MOCK: time-of-day multiplier. Replace with traffic API."""
    hour = departure_dt.hour
    if 7 <= hour < 9:
        return 1.55   # morning rush
    if 17 <= hour < 20:
        return 1.65   # evening rush — worst in Manila
    if 11 <= hour < 13:
        return 1.25   # lunch
    if 9 <= hour < 17:
        return 1.15   # business hours
    if 6 <= hour < 7:
        return 1.10   # early morning
    return 1.00       # off-peak / overnight


def base_duration_min(distance_km: float, factor: float) -> float:
    """MOCK: assume 30 km/h free-flow avg speed in Metro Manila."""
    free_flow_speed = 30.0
    return round((distance_km / (free_flow_speed / factor)) * 60, 1)


def trip_cost_php(distance_km: float, km_per_liter: float, fuel_price_php: float, factor: float) -> float:
    liters_needed = distance_km / km_per_liter
    # Traffic multiplier increases fuel consumption (stop-and-go burns more)
    adjusted_liters = liters_needed * (1 + (factor - 1) * 0.6)
    return round(adjusted_liters * fuel_price_php, 2)


def predict_three_slots(
    origin: str,
    destination: str,
    base_departure: datetime,
    km_per_liter: float,
    fuel_price_php: float,
) -> list[dict]:
    """Return cost predictions for now, +30 min, +60 min."""
    from datetime import timedelta

    distance = road_distance_km(origin, destination)
    slots = []
    for offset_min in [0, 30, 60]:
        dt = base_departure + timedelta(minutes=offset_min)
        factor = traffic_factor(dt)
        cost = trip_cost_php(distance, km_per_liter, fuel_price_php, factor)
        duration = base_duration_min(distance, factor)
        slots.append({
            "label": "Leave now" if offset_min == 0 else f"Leave in {offset_min} min",
            "departure_time": dt.strftime("%I:%M %p"),
            "distance_km": distance,
            "traffic_factor": factor,
            "estimated_duration_min": duration,
            "cost_php": cost,
        })
    return slots


def rank_stations_by_total_cost(
    user_lat: float,
    user_lng: float,
    stations: list[dict],
    fuel_type: str,
    km_per_liter: float,
    radius_km: float = 5.0,
) -> list[dict]:
    """Rank nearby stations by (fuel price + detour cost)."""
    price_key = "gasoline_price_php" if fuel_type == "GASOLINE" else "diesel_price_php"
    results = []
    for s in stations:
        dist = haversine_km(user_lat, user_lng, s["lat"], s["lng"])
        if dist > radius_km:
            continue
        detour_cost = trip_cost_php(dist * 2, km_per_liter, s[price_key], 1.1)
        # Assume filling 20 L
        fill_cost = 20 * s[price_key]
        total_score = fill_cost + detour_cost
        results.append({**s, "distance_km": round(dist, 2), "detour_cost_php": round(detour_cost, 2),
                         "fill_20L_php": round(fill_cost, 2), "total_score": round(total_score, 2)})
    results.sort(key=lambda x: x["total_score"])
    return results
