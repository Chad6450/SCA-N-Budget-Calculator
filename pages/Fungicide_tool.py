import streamlit as st
import sys
import os
from datetime import datetime
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Dummy weather fetch if needed later
from dpird_weather_fetcher import fetch_weather_from_dpird_live
from assess_sclerotinia_risk import assess_sclerotinia_risk, assess_septoria_risk, assess_rust_risk

# --- Fungicide Info ---
fungicide_data = {
    "Canola": {
        "blackleg": [
            {"group": "Group DMI (e.g. Prosaro, Aviator Xpro)", "persistence": "10–21 days", "note": "Protective and curative; apply at 4–6 leaf stage"},
            {"group": "Group SDHI (e.g. Miravis Star)", "persistence": "21–28 days", "note": "Longer residual, better suited for high pressure situations"}
        ]
    },
    "Wheat": {
        "yellow_spot": [
            {"group": "Group DMI (e.g. Prosaro)", "persistence": "10–14 days", "note": "Best applied at early disease onset"},
            {"group": "Group Qol + DMI (e.g. Opera)", "persistence": "12–18 days", "note": "Broad-spectrum and moderately persistent"}
        ]
    },
    "Barley": {
        "rust": [
            {"group": "Group DMI (e.g. Tilt, Prosaro)", "persistence": "10–14 days", "note": "Apply before rust reaches upper canopy"},
            {"group": "Group SDHI + DMI (e.g. Elatus Ace)", "persistence": "18–24 days", "note": "Excellent residual control, especially under rust pressure"}
        ]
    }
}

seed_treatments = [
    "None",
    "Jockey Stayer",
    "Saltro",
    "ILeVO",
    "EverGol Prime",
    "Raxil",
    "Other"
]

foliar_fungicides = [
    "None",
    "Prosaro (Group 3 - DMI)",
    "Aviator Xpro (Group 3+11 - DMI+QoI)",
    "Miravis Star (Group 3+7 - DMI+SDHI)",
    "Tilt (Group 3 - DMI)",
    "Elatus Ace (Group 7+3 - SDHI+DMI)",
    "Opera (Group 11+3 - QoI+DMI)",
    "Other"
]

def display_fungicide_info(crop_type, disease_type):
    st.markdown("### 🧴 Recommended Fungicide Options")
    options = fungicide_data.get(crop_type, {}).get(disease_type, [])
    if not options:
        st.info("No specific fungicide guidance available for this crop/disease.")
    for fung in options:
        st.markdown(f"""
        - **Fungicide Group**: {fung['group']}  
          ⏱ **Persistence**: {fung['persistence']}  
          🧪 **Notes**: {fung['note']}
        """)

# --- Streamlit App UI ---
st.image("sca_logo.jpg", use_container_width=True)
st.markdown("### 🦠 Disease Risk & Fungicide Response – South Coastal Agencies")
crop_type = st.selectbox("🌾 Select Crop Type", ["Canola", "Wheat", "Barley"])

if crop_type == "Canola":
    variety = st.selectbox("Canola Variety", ["43Y92CL", "44Y94CL", "HyTTec Trident", "4540P", "4520P", "Hunter", "Emu", "Py525g", "DG Buller", "Other"])
    disease_type = "blackleg"
    crop_stage = st.selectbox("Crop Stage", ["2-leaf", "3-leaf", "4-leaf", "5-leaf", "6-leaf", "7-leaf", "8-leaf", "Bolting", "10% Flower", "20% Flower", "50% Flower", "Petal Drop"])
elif crop_type == "Wheat":
    variety = st.selectbox("Wheat Variety", ["Scepter", "Vixen", "Rockstar", "Calibre", "Other"])
    disease_type = "yellow_spot"
    crop_stage = st.selectbox("Crop Stage (Zadoks)", ["Z21 - Tillering", "Z30 - Stem Elongation", "Z39 - Flag Leaf", "Z49 - Booting", "Z65 - Flowering"])
else:
    variety = st.selectbox("Barley Variety", ["La Trobe", "Rosalind", "Maximus", "RGT Planet", "Other"])
    disease_type = "rust"
    crop_stage = st.selectbox("Crop Stage (Zadoks)", ["Z21 - Tillering", "Z30 - Stem Elongation", "Z39 - Flag Leaf", "Z49 - Booting", "Z65 - Flowering"])

st.markdown("### 🌱 Agronomic Details")
yield_potential = st.number_input("Expected Yield (t/ha)", min_value=0.0, value=2.5)
grain_price = st.number_input("Grain Price ($/t)", min_value=0.0, value=650.0)
fungicide_cost = st.number_input("Fungicide Cost ($/ha)", min_value=0.0, value=35.0)
application_cost = st.number_input("Application Cost ($/ha)", min_value=0.0, value=12.0)

# --- Weather Inputs ---
st.markdown("### ☔️ Environmental Conditions")
weather_input_mode = st.radio("Select Weather Input Mode", ["Fetch from DPIRD", "Manual Input"])
if weather_input_mode == "Fetch from DPIRD":
    station_code = st.text_input("Enter DPIRD Station Code (e.g. ESP, RAV, SAL)", value="ESP")
    weather = fetch_weather_from_dpird_live(station_code)
    if "error" in weather:
        st.warning(f"⚠️ Could not load weather data: {weather['error']}")
        rain = rh = temp = 0
    else:
        rain = weather["rain_mm"]
        rh = weather["rh_percent"]
        temp = weather["temperature_c"]
else:
    st.markdown("#### Monthly Weather Inputs")
    months = ["May", "June", "July", "August", "September"]
    monthly_rain = {month: st.number_input(f"Rainfall in {month} (mm)", min_value=0.0, value=10.0) for month in months}
    monthly_temp = {month: st.slider(f"Average Temp in {month} (°C)", -5, 50, 16) for month in months}
    monthly_rh = {month: st.slider(f"Average Humidity in {month} (%)", 0, 100, 75) for month in months}
    rain = sum(monthly_rain.values())
    rh = sum(monthly_rh.values()) / len(monthly_rh)
    temp = sum(monthly_temp.values()) / len(monthly_temp)

st.metric("Total Rainfall (mm)", rain)
st.metric("Avg Relative Humidity (%)", rh)
st.metric("Avg Temperature (°C)", temp)

# --- Management History ---
seed_dressed = st.checkbox("Was the seed treated with fungicide?")
selected_seed_treatment = "None"
if seed_dressed:
    selected_seed_treatment = st.selectbox("Select Seed Treatment", seed_treatments)

prior_fungicide = st.checkbox("Has a fungicide already been applied this season?")
selected_prior_fungicide = "None"
if prior_fungicide:
    selected_prior_fungicide = st.selectbox("Select Prior Fungicide", foliar_fungicides)

days_since_rain = st.slider("Days Since Last Rainfall", 0, 14, 3)
leaf_wetness_hours = st.slider("Leaf Wetness (last 7 days)", 0, 50, 24)
rain_days_last_week = st.slider("Rain Days in Last Week", 0, 7, 3)

# --- Evaluate Risk ---
if st.button("🧪 Evaluate Disease Risk & Fungicide ROI"):
    if weather_input_mode == "Fetch from DPIRD" and "error" in weather:
        st.error("⚠️ Weather data unavailable. Cannot evaluate disease risk.")
    else:
        if crop_type == "Canola":
            result = assess_sclerotinia_risk(temp, rh, rain, days_since_rain, leaf_wetness_hours, rain_days_last_week, seed_dressed, prior_fungicide, selected_seed_treatment, selected_prior_fungicide, crop_stage)
        elif crop_type == "Wheat":
            result = assess_septoria_risk(temp, rh, rain, days_since_rain, leaf_wetness_hours, rain_days_last_week, seed_dressed, prior_fungicide, selected_seed_treatment, selected_prior_fungicide, crop_stage)
        else:
            has_resistance = st.checkbox("Does the variety have resistance to rust?", value=False)
            result = assess_rust_risk(temp, rh, crop_stage, has_resistance, seed_dressed, prior_fungicide, selected_seed_treatment, selected_prior_fungicide)

        st.markdown("### ✅ Recommendation")
        st.success(result["recommendation"])
        st.info(f"Risk Level: **{result['risk_level']}**")
        st.markdown("### 🧴 Fungicide Options")
        for f in result["fungicide_options"]:
            st.markdown(f"""
            - **Name**: {f['name']}  
              **Group**: {f['group']}  
              **Persistence**: {f['persistence']}
            """)

        display_fungicide_info(crop_type, disease_type)

st.markdown("---")
st.caption("Developed by South Coastal Agencies")
