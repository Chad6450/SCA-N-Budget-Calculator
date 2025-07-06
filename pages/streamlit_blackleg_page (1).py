
import streamlit as st
from blackleg_risk_tool import evaluate_blackleg_risk

# --- Branding ---
st.image("sca_logo.jpg", use_container_width=True)
st.markdown("### 🦠 Blackleg Risk & Response – South Coastal Agencies")

# --- Agronomic Inputs ---
st.markdown("---")
st.header("1. 🌿 Crop Information")
variety = st.selectbox("Canola Variety", [
    "43Y92CL", "44Y94CL", "HyTTec Trident", "4540P", "4520P",
    "Hunter", "Emu", "Py525g", "DG Buller", "Other"
])
crop_stage = st.selectbox("Crop Stage", ["2-leaf", "3-leaf", "4-leaf", "5-leaf", "6-leaf", "7-leaf", "8-leaf"])
yield_potential = st.number_input("Expected Yield (t/ha)", min_value=0.0, value=2.5, step=0.1)
grain_price = st.number_input("Grain Price ($/t)", min_value=0.0, value=650.0, step=10.0)

# --- Economic Inputs ---
st.header("2. 💰 Fungicide & Application Cost")
fungicide_cost = st.number_input("Fungicide Cost ($/ha)", min_value=0.0, value=35.0, step=1.0)
application_cost = st.number_input("Application Cost ($/ha)", min_value=0.0, value=12.0, step=1.0)

# --- Weather Conditions ---
st.header("3. ☔️ Weather Conditions")
station_code = st.text_input("DPIRD Station Code", value="ESP")
rain_mm = st.number_input("Recent Rainfall (mm)", min_value=0.0, value=6.5, step=0.1)
rh_percent = st.slider("Relative Humidity (%)", min_value=0, max_value=100, value=85)
temperature_c = st.slider("Average Temperature (°C)", min_value=0, max_value=40, value=14)
previous_canola_stubble = st.checkbox("Was Canola Grown Last Year in This Paddock?", value=True)

# --- Run Risk Assessment ---
st.markdown("---")
if st.button("🚨 Evaluate Blackleg Risk"):
    inputs = {
        "variety": variety,
        "crop_stage": crop_stage,
        "yield_potential": yield_potential,
        "grain_price": grain_price,
        "fungicide_cost": fungicide_cost,
        "application_cost": application_cost,
        "rain_mm": rain_mm,
        "rh_percent": rh_percent,
        "temperature_c": temperature_c,
        "previous_canola_stubble": previous_canola_stubble
    }

    result = evaluate_blackleg_risk(inputs)

    st.subheader("📊 Risk Evaluation Result")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Spore Risk", result["spore_risk"])
        st.metric("Recommended Action", result["recommended_action"])
    with col2:
        st.metric("Break-even Yield (kg/ha)", f"{result['break_even_yield']:.0f}")
        st.metric("Yield Potential (t/ha)", result["yield_potential"])

    st.markdown("### 🔬 Variety Profile")
    st.write(f"**Blackleg Resistance Rating**: {result['blackleg_rating']}")
    st.write(f"**Blackleg Group**: {result['blackleg_group']}")

# --- Footer ---
st.markdown("---")
st.caption("Developed in collaboration with South Coastal Agencies")
