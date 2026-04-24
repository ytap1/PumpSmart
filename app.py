import streamlit as st

from utils.db import get_recent_predictions, get_vehicles, init_db

init_db()

st.set_page_config(
    page_title="PumpSmart",
    page_icon="⛽",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Sidebar: vehicle quick-setup ──────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/gas-station.png", width=64)
    st.title("PumpSmart")
    st.caption("AI-powered fuel companion · Metro Manila")
    st.divider()

    st.subheader("Quick Setup")
    km_per_liter = st.number_input("Fuel efficiency (km/L)", min_value=4.0, max_value=30.0, value=st.session_state.get("km_per_liter", 10.0), step=0.5)
    fuel_type = st.selectbox("Fuel type", ["GASOLINE", "DIESEL"])
    fuel_price = st.number_input("Current price (₱/L)", min_value=50.0, max_value=100.0, value=st.session_state.get("fuel_price", 67.50), step=0.10)
    monthly_budget = st.number_input("Monthly fuel budget (₱)", min_value=500, max_value=20000, value=st.session_state.get("monthly_budget", 3000), step=100)
    st.session_state.update({
        "km_per_liter": km_per_liter,
        "fuel_type": fuel_type,
        "fuel_price": fuel_price,
        "monthly_budget": monthly_budget,
    })

    st.divider()
    st.caption("Navigate using the pages in the sidebar above.")

# ── Header ────────────────────────────────────────────────────────────────────
st.title("⛽ PumpSmart Dashboard")
st.caption("Reduce your fuel spend with predictive trip analysis and smart refueling decisions.")

# ── Budget overview ───────────────────────────────────────────────────────────
recent = get_recent_predictions(20)
total_spent = sum(r["predicted_cost_php"] for r in recent)
budget_pct = min(total_spent / monthly_budget * 100, 100) if monthly_budget else 0
remaining = max(monthly_budget - total_spent, 0)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Monthly Budget", f"₱{monthly_budget:,}")
col2.metric("Projected Spend", f"₱{total_spent:,.2f}", delta=f"{budget_pct:.0f}% used", delta_color="inverse" if budget_pct > 80 else "off")
col3.metric("Remaining", f"₱{remaining:,.2f}")
col4.metric("Trips Predicted", len(recent))

# Budget progress bar
st.progress(budget_pct / 100, text=f"Budget used: {budget_pct:.0f}%")

st.divider()

# ── Recent trip predictions ───────────────────────────────────────────────────
col_left, col_right = st.columns([3, 2])

with col_left:
    st.subheader("Recent Trip Predictions")
    if not recent:
        st.info("No predictions yet. Head to **Trip Predictor** to get started.")
    else:
        for r in recent[:5]:
            with st.container(border=True):
                c1, c2, c3 = st.columns([3, 1, 1])
                c1.markdown(f"**{r['route_label']}**")
                c1.caption(f"Depart {r['departure_time']} · {r['distance_km']} km · ~{r['predicted_duration_min']} min")
                c2.metric("Cost", f"₱{r['predicted_cost_php']:.2f}")
                c3.metric("Traffic ×", r["traffic_factor"])

with col_right:
    st.subheader("Quick Tips")
    with st.container(border=True):
        st.markdown("**⏰ Best departure windows today**")
        st.write("• Before 7:00 AM — lightest traffic")
        st.write("• 9:30 AM – 11:00 AM — post-rush window")
        st.write("• After 8:30 PM — evening clears up")
    with st.container(border=True):
        st.markdown("**💡 Fuel price snapshot (mock)**")
        st.write("• Seaoil / Phoenix: ~₱66.50–₱66.80/L")
        st.write("• Caltex: ~₱67.20/L")
        st.write("• Petron / Shell: ~₱67.50–₱68.10/L")

st.divider()
st.caption("PumpSmart MVP · Mock data active · Add GOOGLE_API_KEY in Streamlit secrets for live AI.")
