import folium
from utils.fuel_calc import MANILA_AREAS

BRAND_COLORS = {
    "Petron": "red",
    "Shell": "yellow",
    "Caltex": "blue",
    "Phoenix": "orange",
    "Seaoil": "green",
}


def route_map(origin: str, destination: str) -> folium.Map:
    coords1 = MANILA_AREAS.get(origin, (14.5547, 121.0244))
    coords2 = MANILA_AREAS.get(destination, (14.5547, 121.0244))
    center_lat = (coords1[0] + coords2[0]) / 2
    center_lng = (coords1[1] + coords2[1]) / 2

    m = folium.Map(location=[center_lat, center_lng], zoom_start=12, tiles="CartoDB dark_matter")

    folium.Marker(
        coords1, tooltip=f"Origin: {origin}",
        icon=folium.Icon(color="green", icon="play", prefix="fa"),
    ).add_to(m)
    folium.Marker(
        coords2, tooltip=f"Destination: {destination}",
        icon=folium.Icon(color="red", icon="flag", prefix="fa"),
    ).add_to(m)

    # MOCK_ROUTE: straight dashed line — replace with Directions API polyline
    folium.PolyLine(
        [coords1, coords2],
        color="#FF6B35", weight=3, dash_array="8 4",
        tooltip="MOCK route — real path via Directions API",
    ).add_to(m)

    return m


def stations_map(user_lat: float, user_lng: float, stations: list[dict], ranked: list[dict]) -> folium.Map:
    m = folium.Map(location=[user_lat, user_lng], zoom_start=14, tiles="CartoDB dark_matter")

    folium.Marker(
        [user_lat, user_lng],
        tooltip="Your location",
        icon=folium.Icon(color="blue", icon="car", prefix="fa"),
    ).add_to(m)

    ranked_ids = {s["id"]: i + 1 for i, s in enumerate(ranked)}

    for s in stations:
        color = BRAND_COLORS.get(s["brand"], "gray")
        rank = ranked_ids.get(s["id"])
        label = f"#{rank} " if rank else ""
        folium.Marker(
            [s["lat"], s["lng"]],
            tooltip=f"{label}{s['name']} — ₱{s['gasoline_price_php']:.2f}/L gas",
            icon=folium.Icon(color=color, icon="tint", prefix="fa"),
        ).add_to(m)

    return m
