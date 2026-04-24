from datetime import datetime

import streamlit as st
from streamlit_folium import st_folium

from utils.db import init_db, save_prediction
from utils.fuel_calc import MANILA_AREAS, predict_three_slots
from utils.maps import route_map

init_db()

st.set_page_config(page_title="Trip Predictor — PumpSmart", page_icon="🗺️", layout="wide")
st.title("🗺️ Trip Cost Predictor")
st.caption("Compare fuel cost across 3 departure windows. MOCK route distance — real Directions API coming soon.")

# ── Sidebar: vehicle ──────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Your Vehicle")
    km_per_liter = st.number_input("Fuel efficiency (km/L)", min_value=4.0, max_value=30.0, value=st.session_state.get("km_per_liter", 10.0), step=0.5)
    fuel_type = st.selectbox("Fuel type", ["GASOLINE", "DIESEL"], index=0 if st.session_state.get("fuel_type", "GASOLINE") == "GASOLINE" else 1)
    fuel_price = st.number_input("Current fuel price (₱/L)", min_value=50.0, max_value=100.0, value=st.session_state.get("fuel_price", 67.50), step=0.10)
    st.session_state["km_per_liter"] = km_per_liter
    st.session_state["fuel_type"] = fuel_type
    st.session_state["fuel_price"] = fuel_price

areas = list(MANILA_AREAS.keys())

col1, col2 = st.columns(2)
with col1:
    origin = st.selectbox("Origin", areas, index=0)
with col2:
    dest_options = [a for a in areas if a != origin]
    destination = st.selectbox("Destination", dest_options, index=2)

departure_time = st.time_input("Planned departure time", value=datetime.now().time())
departure_dt = datetime.combine(datetime.today(), departure_time)

if st.button("Predict Trip Cost", type="primary", use_container_width=True):
    if origin == destination:
        st.error("Origin and destination must be different.")
    else:
        slots = predict_three_slots(origin, destination, departure_dt, km_per_liter, fuel_price)

        st.subheader("Cost Comparison")
        cols = st.columns(3)
        cheapest_cost = min(s["cost_php"] for s in slots)
        for i, slot in enumerate(slots):
            with cols[i]:
                saving = slots[0]["cost_php"] - slot["cost_php"]
                saving_label = f"Save ₱{saving:.2f}" if saving > 0 else ("Baseline" if saving == 0 else f"+₱{abs(saving):.2f}")
                st.metric(
                    label=slot["label"],
                    value=f"₱{slot['cost_php']:.2f}",
                    delta=saving_label if i > 0 else None,
                    delta_color="normal",
                )
                st.caption(
                    f"Depart {slot['departure_time']} · "
                    f"{slot['distance_km']} km · "
                    f"~{slot['estimated_duration_min']} min · "
                    f"Traffic ×{slot['traffic_factor']}"
                )

        best = min(slots, key=lambda s: s["cost_php"])
        if best["label"] != "Leave now":
            st.success(f"Tip: {best['label']} saves you ₱{slots[0]['cost_php'] - best['cost_php']:.2f} vs leaving now.")
        else:
            st.info("Now is already the cheapest window for this trip.")

        st.subheader("Route Map")
        st.caption("⚠️ MOCK_ROUTE — dashed line is straight-line approximation, not real road path.")
        m = route_map(origin, destination)
        st_folium(m, width="100%", height=380)

        # Persist best prediction
        save_prediction(
            vehicle_id=st.session_state.get("vehicle_id", 0),
            route_label=f"{origin} → {destination}",
            departure_time=best["departure_time"],
            distance_km=best["distance_km"],
            predicted_cost_php=best["cost_php"],
            predicted_duration_min=best["estimated_duration_min"],
            traffic_factor=best["traffic_factor"],
        )
