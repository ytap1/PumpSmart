import streamlit as st
from streamlit_folium import st_folium

from utils.db import get_all_stations, init_db
from utils.fuel_calc import MANILA_AREAS, rank_stations_by_total_cost
from utils.maps import stations_map

init_db()

st.set_page_config(page_title="Refuel Advisor — PumpSmart", page_icon="⛽", layout="wide")
st.title("⛽ Smart Refuel Advisor")
st.caption("Find the cheapest nearby station factoring in detour cost, not just pump price.")

with st.sidebar:
    st.header("Your Vehicle")
    km_per_liter = st.number_input("Fuel efficiency (km/L)", min_value=4.0, max_value=30.0, value=st.session_state.get("km_per_liter", 10.0), step=0.5)
    fuel_type = st.selectbox("Fuel type", ["GASOLINE", "DIESEL"], index=0 if st.session_state.get("fuel_type", "GASOLINE") == "GASOLINE" else 1)
    st.session_state["km_per_liter"] = km_per_liter
    st.session_state["fuel_type"] = fuel_type

areas = list(MANILA_AREAS.keys())

if "tank_level" not in st.session_state:
    st.session_state["tank_level"] = 30
if "search_radius_km" not in st.session_state:
    st.session_state["search_radius_km"] = 5.0

col1, col2 = st.columns(2)
with col1:
    location = st.selectbox("Your current location", areas, index=0)
with col2:
    tank_level = st.slider("Tank level (%)", min_value=0, max_value=100, value=st.session_state["tank_level"], step=5)
st.session_state["tank_level"] = tank_level

radius_km = st.slider("Search radius (km)", min_value=1.0, max_value=10.0, value=st.session_state["search_radius_km"], step=0.5)
st.session_state["search_radius_km"] = radius_km

if st.button("Find Best Station", type="primary", use_container_width=True):
    user_lat, user_lng = MANILA_AREAS[location]
    all_stations = get_all_stations()
    ranked = rank_stations_by_total_cost(user_lat, user_lng, all_stations, fuel_type, km_per_liter, radius_km)

    if not ranked:
        st.warning(f"No stations found within {radius_km} km of {location}. Try increasing the radius.")
        st.session_state.pop("refuel_result", None)
    else:
        price_key = "gasoline_price_php" if fuel_type == "GASOLINE" else "diesel_price_php"
        best = ranked[0]
        worst = ranked[-1]
        st.session_state["refuel_result"] = {
            "ranked": ranked,
            "all_stations": all_stations,
            "user_lat": user_lat,
            "user_lng": user_lng,
            "fuel_type": fuel_type,
            "price_key": price_key,
            "best": best,
            "worst": worst,
            "savings": worst["fill_20L_php"] - best["fill_20L_php"],
            "tank_level": tank_level,
        }

result = st.session_state.get("refuel_result")
if result:
    ranked = result["ranked"]
    best = result["best"]
    worst = result["worst"]
    price_key = result["price_key"]

    st.success(
        f"**Refuel at {best['name']}** ({best['distance_km']} km away) · "
        f"₱{best[price_key]:.2f}/L · Fill 20L for ₱{best['fill_20L_php']:.2f}"
    )
    if result["savings"] > 0 and len(ranked) > 1:
        st.info(f"Saves ₱{result['savings']:.2f} vs {worst['name']} on a 20L fill.")

    if result["tank_level"] <= 15:
        st.error("Tank critically low — refuel now regardless of price.")
    elif result["tank_level"] <= 30:
        st.warning("Tank below 30% — recommended to refuel at the best nearby station.")
    else:
        st.info("Tank level OK — you can afford to wait for a better price on your route.")

    st.subheader(f"Nearby Stations ({len(ranked)} found)")
    for i, s in enumerate(ranked):
        badge = "🥇" if i == 0 else ("🥈" if i == 1 else "🥉" if i == 2 else f"#{i+1}")
        with st.expander(f"{badge} {s['name']} — ₱{s[price_key]:.2f}/L · {s['distance_km']} km away"):
            c1, c2, c3 = st.columns(3)
            c1.metric("Pump price", f"₱{s[price_key]:.2f}/L")
            c2.metric("Detour cost", f"₱{s['detour_cost_php']:.2f}")
            c3.metric("Fill 20L (total score)", f"₱{s['total_score']:.2f}")

    st.subheader("Station Map")
    m = stations_map(result["user_lat"], result["user_lng"], result["all_stations"], ranked)
    st_folium(m, width="100%", height=400)
