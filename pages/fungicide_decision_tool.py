import streamlit as st
import sys
import os
from datetime import datetime
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# --- Required Modules ---
from dpird_weather_fetcher import fetch_weather_from_dpird_live
from assess_sclerotinia_risk import assess_sclerotinia_risk
from assess_septoria_risk import assess_septoria_risk
from assess_rust_risk import assess_rust_risk
from blackleg_risk_model import evaluate_blackleg_risk  # Assumes this function is available
from variety_blackleg_data import variety_resistance_ratings  # Assumes this dict is available

# --- Fungicide Info ---
fungicide_data = {
    "Canola": {
        "blackleg": [
            {"group": "Group DMI (e.g. Prosaro, Aviator Xpro)", "persistence": "10–21 days", "note": "Protective and curative; apply at 4–6 leaf stage"},
            {"group": "Group SDHI (e.g. Miravis Star)", "persistence": "21–28 days", "note": "Longer residual, better suited for high pressure situations"}
        ]
    }
}

seed_treatments = [
    {"name": "None", "group": ""},
    {"name": "Jockey Stayer", "group": "Group 3 - DMI"},
    {"name": "Saltro", "group": "Group 7 - SDHI"},
    {"name": "Other", "group": "Check label"}
]

foliar_fungicides = [
    {"name": "None", "group": ""},
    {"name": "Prosaro", "group": "Group 3 - DMI"},
    {"name": "Miravis Star", "group": "Group 3+7 - DMI+SDHI"},
    {"name": "Other", "group": "Check label"}
]

# --- Streamlit UI ---
st.image("sca_logo.jpg", use_container_width=True)
st.markdown("### 🦠 Disease Risk & Fungicide Response – South Coastal Agencies")

crop_type = st.selectbox("🌾 Select Crop Type", ["Canola", "Wheat", "Barley"])

# --- Weather Section ---
st.markdown("### ☔️ Environmental Conditions")
weather_input_mode = st.radio("Select Weather Input Mode", ["Fetch from DPIRD", "Manual Input"])
if weather_input_mode == "Fetch from DPIRD":
    station_code = st.text_input("Enter DPIRD Station Code (e.g. ESP, RAV, SAL)", value="ESP")
    weather = fetch_weather_from_dpird_live(station_code)
    if "error" in weather:
        st.error(f"⚠️ Weather fetch failed: {weather['error']}")
        st.stop()
    else:
        rain = weather["rain_mm"]
        rh = weather["rh_percent"]
        temp = weather["temperature_c"]
else:
    months = ["May", "June", "July", "August", "September"]
    monthly_rain = {m: st.number_input(f"Rainfall in {m} (mm)", min_value=0.0, value=10.0) for m in months}
    monthly_temp = {m: st.slider(f"Avg Temp in {m} (°C)", -5, 50, 16) for m in months}
    monthly_rh = {m: st.slider(f"Avg RH in {m} (%)", 0, 100, 75) for m in months}
    rain = sum(monthly_rain.values())
    rh = sum(monthly_rh.values()) / len(monthly_rh)
    temp = sum(monthly_temp.values()) / len(monthly_temp)

st.metric("Total Rainfall (mm)", rain)
st.metric("Avg Relative Humidity (%)", rh)
st.metric("Avg Temperature (°C)", temp)

# --- Canola Crop Specific Blackleg Logic ---
if crop_type == "Canola":
    st.markdown("### ⚫️ Blackleg Risk Inputs")

    variety = st.selectbox("Canola Variety", list(variety_resistance_ratings.keys()))
    crop_stage = st.selectbox("Crop Stage", ["2-leaf", "3-leaf", "4-leaf", "5-leaf", "6-leaf", "7-leaf", "8-leaf", "Bolting", "10% Flower", "20% Flower", "50% Flower", "Petal Drop"])
    yield_potential = st.slider("Estimated Yield Potential (t/ha)", 0.5, 5.0, 2.5, 0.1)
    grain_price = st.number_input("Grain Price ($/t)", min_value=100.0, value=650.0)
    fungicide_cost = st.number_input("Fungicide Cost ($/ha)", min_value=0.0, value=35.0)
    application_cost = st.number_input("Application Cost ($/ha)", min_value=0.0, value=12.0)
    rain_mm = st.slider("Recent Rainfall (mm)", 0.0, 50.0, 6.0, 0.5)
    rh_percent = st.slider("Relative Humidity (%)", 0, 100, 85)
    temperature_c = st.slider("Temperature (°C)", 0, 40, 14)
    same_group_as_last_year = st.checkbox("Same Blackleg Group Used as Last Year?", value=False)
    same_crop_2_years = st.checkbox("Same Paddock Grown to Canola Last 2 Years?", value=False)
    lesions_visible = st.checkbox("Are lesions currently visible on plants?", value=False)
    rain_forecast_hours = st.slider("Rain Forecast (Next 7 Days - Hours of Rain)", 0, 168, 24)
    selected_seed_treatment = st.selectbox("Seed Treatment Product", [s["name"] for s in seed_treatments])
    selected_prior_fungicide = st.selectbox("Prior Foliar Fungicide", [f["name"] for f in foliar_fungicides])

    if st.button("🦠 Assess Blackleg Risk"):
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
            "same_group_as_last_year": same_group_as_last_year,
            "same_crop_2_years": same_crop_2_years,
            "lesions_visible": lesions_visible,
            "rain_forecast_hours": rain_forecast_hours,
            "seed_treatment": selected_seed_treatment,
            "prior_fungicide": selected_prior_fungicide
        }

        result = evaluate_blackleg_risk(inputs)
        st.subheader("🧾 Blackleg Risk Result")
        st.markdown(f"**Blackleg Rating**: {result['blackleg_rating']}")
        st.markdown(f"**Resistance Group**: {result['blackleg_group']}")
        st.markdown(f"**Spore Release Risk**: {result['spore_risk']}")
        st.markdown(f"**Break-even Yield**: {result['break_even_yield']} kg/ha")
        st.markdown(f"**Recommendation**: {result['recommended_action']}")

        if result.get("warnings"):
            st.warning("⚠️ AFREN Warnings:")
            for warn in result["warnings"]:
                st.markdown(f"- {warn}")

        if result.get("fungicide_options"):
            st.markdown("### 🧴 Compliant Fungicide Options")
            for f in result["fungicide_options"]:
                st.markdown(f"""
                - **Name**: {f['name']}  
                  **Group**: {f['group']}  
                  **Persistence**: {f['persistence']}
                """)

# --- Other Crops (Wheat/Barley) ---
else:
    if crop_type == "Wheat":
        variety = st.selectbox("Wheat Variety", ["Scepter", "Vixen", "Rockstar", "Calibre", "Other"])
        disease_type = "yellow_spot"
        crop_stage = st.selectbox("Crop Stage (Zadoks)", ["Z21 - Tillering", "Z30 - Stem Elongation", "Z39 - Flag Leaf", "Z49 - Booting", "Z65 - Flowering"])
    else:
        variety = st.selectbox("Barley Variety", ["La Trobe", "Rosalind", "Maximus", "RGT Planet", "Other"])
        disease_type = "rust"
        crop_stage = st.selectbox("Crop Stage (Zadoks)", ["Z21 - Tillering", "Z30 - Stem Elongation", "Z39 - Flag Leaf", "Z49 - Booting", "Z65 - Flowering"])

    seed_dressed = st.checkbox("Was the seed treated with fungicide?")
    selected_seed_treatment = {"name": "None", "group": ""}
    if seed_dressed:
        selected_name = st.selectbox("Select Seed Treatment", [s["name"] for s in seed_treatments])
        selected_seed_treatment = next(s for s in seed_treatments if s["name"] == selected_name)

    prior_fungicide = st.checkbox("Has a fungicide already been applied this season?")
    selected_prior_fungicide = {"name": "None", "group": ""}
    if prior_fungicide:
        selected_name = st.selectbox("Select Prior Fungicide", [f["name"] for f in foliar_fungicides])
        selected_prior_fungicide = next(f for f in foliar_fungicides if f["name"] == selected_name)

    days_since_rain = st.slider("Days Since Last Rainfall", 0, 14, 3)
    leaf_wetness_hours = st.slider("Leaf Wetness (last 7 days)", 0, 50, 24)
    rain_days_last_week = st.slider("Rain Days in Last Week", 0, 7, 3)

    if st.button("🧪 Evaluate Disease Risk & Fungicide ROI"):
        if crop_type == "Wheat":
            result = assess_septoria_risk(temp, rh, rain, days_since_rain, leaf_wetness_hours,
                                          rain_days_last_week, seed_dressed, prior_fungicide,
                                          selected_seed_treatment["name"], selected_prior_fungicide["name"], crop_stage)
        else:
            has_resistance = st.checkbox("Does the variety have resistance to rust?", value=False)
            result = assess_rust_risk(temp, rh, crop_stage, has_resistance,
                                      seed_dressed, prior_fungicide,
                                      selected_seed_treatment["name"], selected_prior_fungicide["name"])

        st.markdown("### ✅ Recommendation")
        st.success(result["recommendation"])
        st.info(f"Risk Level: **{result['risk_level']}**")

        st.markdown("### 🧴 Fungicide Options")
        if result.get("fungicide_options"):
            for f in result["fungicide_options"]:
                st.markdown(f"""
                - **Name**: {f['name']}  
                  **Group**: {f['group']}  
                  **Persistence**: {f['persistence']}
                """)
        else:
            st.info("No fungicide recommendations available.")
