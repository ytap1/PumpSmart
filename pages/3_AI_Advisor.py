import streamlit as st

from utils.ai_client import MOCK_WARNING, get_recommendations
from utils.db import get_recent_predictions, init_db

init_db()

st.set_page_config(page_title="AI Advisor — PumpSmart", page_icon="🤖", layout="wide")
st.title("🤖 AI Fuel Savings Advisor")
st.caption("Powered by Gemma 4 26B A4B via Google AI Studio.")

with st.sidebar:
    st.header("Your Profile")
    monthly_budget = st.number_input("Monthly fuel budget (₱)", min_value=500, max_value=20000, value=st.session_state.get("monthly_budget", 3000), step=100)
    km_per_liter = st.number_input("Fuel efficiency (km/L)", min_value=4.0, max_value=30.0, value=st.session_state.get("km_per_liter", 10.0), step=0.5)
    fuel_type = st.selectbox("Fuel type", ["GASOLINE", "DIESEL"], index=0 if st.session_state.get("fuel_type", "GASOLINE") == "GASOLINE" else 1)
    vehicle_desc = st.text_input("Vehicle (e.g. Toyota Vios 2020)", value=st.session_state.get("vehicle_desc", ""))
    commute_pattern = st.selectbox("Primary commute pattern", ["Daily office (EDSA)", "WFH 3x/week", "Weekends only", "Irregular"])
    st.session_state.update({
        "monthly_budget": monthly_budget,
        "km_per_liter": km_per_liter,
        "fuel_type": fuel_type,
        "vehicle_desc": vehicle_desc,
    })

recent = get_recent_predictions(5)
avg_trip_cost = round(sum(r["predicted_cost_php"] for r in recent) / len(recent), 2) if recent else 0
monthly_projected = round(avg_trip_cost * 20, 2) if recent else 0

context = {
    "vehicle": vehicle_desc or f"Unknown vehicle, {km_per_liter} km/L",
    "fuel_type": fuel_type,
    "km_per_liter": km_per_liter,
    "monthly_budget_php": monthly_budget,
    "monthly_projected_spend_php": monthly_projected,
    "avg_trip_cost_php": avg_trip_cost,
    "recent_trips_count": len(recent),
    "commute_pattern": commute_pattern,
    "over_budget": monthly_projected > monthly_budget,
}

st.subheader("Context Summary")
col1, col2, col3 = st.columns(3)
col1.metric("Monthly Budget", f"₱{monthly_budget:,}")
col2.metric("Projected Spend", f"₱{monthly_projected:,}", delta=f"₱{monthly_projected - monthly_budget:+,.0f}" if monthly_projected else None, delta_color="inverse")
col3.metric("Avg Trip Cost", f"₱{avg_trip_cost:,.2f}" if avg_trip_cost else "—")

st.divider()

if st.button("Get AI Recommendations", type="primary", use_container_width=True):
    with st.spinner("Gemma is analyzing your driving profile..."):
        recommendations, is_mock = get_recommendations(context)
    st.session_state["ai_result"] = {"recommendations": recommendations, "is_mock": is_mock}

ai_result = st.session_state.get("ai_result")
if ai_result:
    recommendations = ai_result["recommendations"]

    if ai_result["is_mock"]:
        st.warning(MOCK_WARNING)

    st.subheader("Your 3 Fuel-Saving Recommendations")

    category_icons = {"timing": "⏰", "routing": "🗺️", "behavior": "💡"}

    for i, rec in enumerate(recommendations):
        icon = category_icons.get(rec.get("category", ""), "💡")
        with st.container(border=True):
            col_title, col_saving = st.columns([3, 1])
            with col_title:
                st.markdown(f"**{icon} {rec['title']}**")
                st.caption(f"Category: {rec.get('category', '—').capitalize()}")
            with col_saving:
                st.metric("Est. monthly saving", f"₱{rec.get('estimated_savings_php', 0):,}")
            st.write(rec["recommendation"])

    total_savings = sum(r.get("estimated_savings_php", 0) for r in recommendations)
    st.success(f"Following all 3 tips could save you ~₱{total_savings:,}/month.")
