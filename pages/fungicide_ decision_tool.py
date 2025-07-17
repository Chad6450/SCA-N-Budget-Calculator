import streamlit as st
import sys
import os
import pandas as pd
from datetime import datetime

# Hide sidebar
st.markdown("""
    <div style="text-align: right; margin-top: -50px;">
        <a href="/Home" style="
            text-decoration: none;
            font-weight: bold;
            font-size: 16px;
            color: #004D40;
            border: 2px solid #004D40;
            padding: 8px 16px;
            border-radius: 12px;
            background-color: #E0F2F1;
            box-shadow: 2px 2px 4px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
        ">
            🏠 Home
        </a>
    </div>
""", unsafe_allow_html=True)

# Enable module imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from dpird_weather_fetcher import fetch_weather_from_dpird_live
from assess_disease_risks import assess_sclerotinia_risk, assess_septoria_risk, assess_rust_risk

# --- HEADER ---
st.image("sca_logo.jpg", use_container_width=True)
st.markdown("### 🦠 Disease Risk & Fungicide Response – South Coastal Agencies")
# Reference Data
seed_treatment_lookup = {
    "None": {"group": "", "moa": ""},
    "Saltro": {"group": "Group 7", "moa": "SDHI"},
    "ILeVO": {"group": "Group 7", "moa": "SDHI"},
    "Flutriafol": {"group": "Group 3", "moa": "DMI"},
    "Jocky": {"group": "Group 3", "moa": "DMI"},
    "Vibrance": {"group": "Group 7", "moa": "SDHI"},
    "EverGol Extend": {"group": "Group 7", "moa": "SDHI"},
    "EverGol Energy": {"group": "Group 7", "moa": "SDHI"},
}

foliar_fungicide_lookup = {
    "None": {"group": "", "moa": ""},
    "Prothio T": {"group": "Group 3", "moa": "DMI"},
    "Aviator Xpro": {"group": "Group 3+11", "moa": "DMI + QoI"},
    "Miravis Star": {"group": "Group 3+7", "moa": "DMI + SDHI"},
    "Elatus Ace": {"group": "Group 7+11", "moa": "SDHI + QoI"},
    "Miravis": {"group": "Group 7", "moa": "SDHI"},
    "Azoxy Xtra": {"group": "Group 11 + 3", "moa": "DMI + QoI"},
    "Epoxiconazole": {"group": "Group 3", "moa": "DMI"},
    "Veritas Opti": {"group": "Group 3 + 11 + 29", "moa": "DMI + QoI"},
}

fungicide_costs = {
    "Prosaro": {"cost_per_ha": 35, "rate": "150 mL/ha", "action": "Curative + Protective"},
    "Aviator Xpro": {"cost_per_ha": 38, "rate": "300 mL/ha", "action": "Curative + Protective"},
    "Miravis Star": {"cost_per_ha": 42, "rate": "500 mL/ha", "action": "Protective"},
    "Elatus Ace": {"cost_per_ha": 40, "rate": "300 mL/ha", "action": "Protective"},
    "Miravis": {"cost_per_ha": 36, "rate": "200 mL/ha", "action": "Protective"},
    "Azoxy Xtra": {"cost_per_ha": 33, "rate": "300 mL/ha", "action": "Curative + Protective"},
    "Epoxiconazole": {"cost_per_ha": 28, "rate": "250 mL/ha", "action": "Curative"},
    "Veritas Opti": {"cost_per_ha": 48, "rate": "750 mL/ha", "action": "Protective"},
}

def count_sdhi_uses(seed_treatment, prior_fungicide):
    seed_sdhi = "sdhi" in seed_treatment_lookup.get(seed_treatment, {}).get("moa", "").lower()
    foliar_sdhi = "sdhi" in foliar_fungicide_lookup.get(prior_fungicide, {}).get("moa", "").lower()
    return int(seed_sdhi) + int(foliar_sdhi)

# Crop type & growth stage
crop_type = st.selectbox("🌾 Select Crop Type", ["Canola", "Wheat", "Barley"])
if crop_type == "Canola":
    variety = st.selectbox("Canola Variety", ["Hunter", "Emu", "4540P", "4520P", "Other"])
    crop_stage = st.selectbox("Crop Stage", ["2-leaf", "4-leaf", "6-leaf", "10% Flower", "50% Flower", "Petal Drop"])
elif crop_type == "Wheat":
    variety = st.selectbox("Wheat Variety", ["Scepter", "Vixen", "Other"])
    crop_stage = st.selectbox("Crop Stage (Zadoks)", ["Z21", "Z30", "Z39", "Z49", "Z65"])
else:
    variety = st.selectbox("Barley Variety", ["La Trobe", "RGT Planet", "Other"])
    crop_stage = st.selectbox("Crop Stage (Zadoks)", ["Z21", "Z30", "Z39", "Z49", "Z65"])

# Agronomic & Economic Inputs
st.markdown("### 🌱 Agronomic Details")
yield_potential = st.number_input("Expected Yield (t/ha)", value=2.5)
default_grain_price = 850 if crop_type == "Canola" else 350 if crop_type == "Wheat" else 320
grain_price = st.number_input("Grain Price ($/t)", value=default_grain_price)
application_cost = st.number_input("Application Cost ($/ha)", value=12.0)
# Step 1: Ask if disease is already present
disease_present = st.checkbox("Is disease already present in the crop?")

# Step 2: If yes, show disease types based on crop
if disease_present:
    disease_options_by_crop = {
        "Canola": ["Blackleg", "Sclerotinia"],
        "Wheat": ["Yellow Spot", "Septoria", "Powdery Mildew", "Rust"],
        "Barley": ["Net Blotch", "Powdery Mildew", "Rust"]
    }
    selected_disease = st.selectbox("Select Disease Type", disease_options_by_crop[crop_type])
else:
    selected_disease = None

# Weather
st.markdown("### ☔️ Environmental Conditions")
weather_input_mode = st.radio("Select Weather Input Mode", ["Fetch from DPIRD", "Manual Input"])
if weather_input_mode == "Fetch from DPIRD":
    station_code = st.text_input("Enter DPIRD Station Code", value="ESP")
    weather = fetch_weather_from_dpird_live(station_code)
    if "error" in weather:
        st.warning(f"⚠️ Could not load weather data: {weather['error']}")
        rain = rh = temp = 0
    else:
        rain = weather["rain_mm"]
        rh = weather["rh_percent"]
        temp = weather["temperature_c"]
else:
    months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    def display_weather_inputs(title, key_prefix, min_val, max_val, default_val, step_val):
        st.subheader(title)
        values = {}
        for i in range(0, len(months), 4):
            cols = st.columns(4)
            for j, col in enumerate(cols):
                if i + j < len(months):
                    month = months[i + j]
                    with col:
                        values[month] = st.number_input(
                            f"{month}", key=f"{key_prefix}_{month}",
                            min_value=min_val, max_value=max_val,
                            value=default_val, step=step_val
                        )
        return values

    monthly_rain = display_weather_inputs("☔ Rainfall (mm)", "rain", 0.0, 1000.0, 10.0, 1.0)
    monthly_rh = display_weather_inputs("💧 Relative Humidity (%)", "rh", 0.0, 100.0, 75.0, 1.0)
    monthly_temp = display_weather_inputs("🌡 Temperature (°C)", "temp", -10.0, 50.0, 16.0, 0.5)
    rain = sum(monthly_rain.values())
    rh = sum(monthly_rh.values()) / len(monthly_rh)
    temp = sum(monthly_temp.values()) / len(monthly_temp)

st.metric("Total Rainfall (mm)", rain)
st.metric("Avg Relative Humidity (%)", rh)
st.metric("Avg Temperature (°C)", temp)

# Seed & prior fungicide selection
seed_dressed = st.checkbox("Seed Treated?")
selected_seed_treatment = "None"
if seed_dressed:
    seed_options = [f"{name} ({data['group']} – {data['moa']})" for name, data in seed_treatment_lookup.items()]
    selected_seed_treatment_display = st.selectbox("Select Seed Treatment", seed_options)
    selected_seed_treatment = selected_seed_treatment_display.split(" (")[0]

prior_fungicide = st.checkbox("Foliar Fungicide Applied to Date?")
selected_prior_fungicide = "None"
if prior_fungicide:
    foliar_options = [f"{name} ({data['group']} – {data['moa']})" for name, data in foliar_fungicide_lookup.items()]
    selected_prior_fungicide_display = st.selectbox("Select Prior Foliar Fungicide", foliar_options)
    selected_prior_fungicide = selected_prior_fungicide_display.split(" (")[0]

days_since_rain = st.slider("Days Since Last Rain", 0, 14, 3)
leaf_wetness_hours = st.slider("Leaf Wetness (last 7 days)", 0, 50, 24)
rain_days_last_week = st.slider("Rain Days Last Week", 0, 7, 3)

# --- EVALUATE BUTTON ---
fungicide_options = []
if st.button("🧪 Evaluate Disease Risk & Fungicide ROI"):
    if weather_input_mode == "Fetch from DPIRD" and "error" in weather:
        st.error("⚠️ Weather data unavailable.")
    else:
        if crop_type == "Canola":
            result = assess_sclerotinia_risk(temp, rh, rain, days_since_rain, leaf_wetness_hours,
                rain_days_last_week, seed_dressed, prior_fungicide,
                selected_seed_treatment, selected_prior_fungicide, crop_stage)
        elif crop_type == "Wheat":
            result = assess_septoria_risk(temp, rh, rain, crop_stage, False,
                seed_dressed, prior_fungicide, selected_seed_treatment, selected_prior_fungicide)
        else:
            result = assess_rust_risk(temp, rh, crop_stage, False,
                seed_dressed, prior_fungicide, selected_seed_treatment, selected_prior_fungicide)

        st.markdown("### ✅ Recommendation")
        st.success(result["recommendation"])
        st.info(f"Risk Level: **{result['risk_level']}**")

        fungicide_options = result.get("fungicide_options", [])
        if count_sdhi_uses(selected_seed_treatment, selected_prior_fungicide) >= 2:
            fungicide_options = [
                f for f in fungicide_options
                if "SDHI" not in f["group"].upper() and "GROUP 7" not in f["group"].upper()
            ]
            st.warning("⚠️ Two SDHI applications already used. SDHI options excluded per AFREN guidelines.")

        # Build table
        table = []  # ✅ Make sure this line exists
if disease_present:
    fungicide_options = [
        f for f in fungicide_options
        if "curative" in fungicide_costs.get(f["name"], {}).get("action", "").lower()
    ]

table = []
for f in fungicide_options:
    name = f['name']
    group = f['group']
    persistence = f['persistence']

    if name in fungicide_costs:
        rate = fungicide_costs[name]["rate"]
        cost = fungicide_costs[name]["cost_per_ha"]
        action = fungicide_costs[name]["action"]
        total_cost = cost + application_cost
        be_yield = total_cost / (grain_price / 1000)
    else:
        rate = "-"
        action = "-"
        total_cost = 0
        be_yield = "N/A"

    table.append({
        "Fungicide": name,
        "Group": group,
        "Persistence": persistence,
        "Rate": rate,
        "Mode of Action": action,
        "Cost/ha ($)": f"${total_cost:.2f}",
        "Break-even Yield (kg/ha)": be_yield if isinstance(be_yield, str) else f"{be_yield:.1f}"
    })

st.markdown("### 📊 Fungicide Comparison Table")
st.dataframe(pd.DataFrame(table))

st.markdown("---")
st.caption("Developed by South Coastal Agencies")
