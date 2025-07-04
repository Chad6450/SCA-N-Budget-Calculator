import streamlit as st
import pandas as pd

# --- Branding ---
st.image("sca_logo.jpg", use_container_width=True)
st.markdown("### Nitrogen Budget Calculator – South Coastal Agencies")

# --- Agronomic Inputs ---
st.header("1. Yield Expectations")
crop_type = st.selectbox("Crop Type", ["Wheat", "Barley", "Oats", "Canola"])

# Set label and default value based on crop type
if crop_type.lower() == "canola":
    label = "Target Oil (%)"
    default_value = 42.0
else:
    label = "Target Protein (%)"
    default_value = 11.5

col1, col2 = st.columns(2)
with col1:
    yield_t_ha = st.number_input("Expected Yield (t/ha)", min_value=0.0, value=4.0, step=0.1)
with col2:
    protein_or_oil = st.number_input(label, min_value=0.0, value=default_value, step=0.1)

nue = st.slider("Nitrogen Use Efficiency (NUE)", min_value=0.1, max_value=1.0, value=0.6, step=0.05)

# --- Soil Test Inputs ---
st.header("2. Soil Test Data")
col3, col4 = st.columns(2)
with col3:
    nitrate = st.number_input("Nitrate-N (mg/kg)", min_value=0.0, value=5.0)
with col4:
    ammonia = st.number_input("Ammonia-N (mg/kg)", min_value=0.0, value=2.0)

organic_n = st.number_input("Organic N Pool (kg/ha)", min_value=0.0, value=1560.0)

# --- Rainfall Data Placeholder ---
st.header("3. Rainfall (Example Placeholder)")
station_code = st.text_input("Enter DPIRD Station Code", value="ESP")

@st.cache_data
def get_rainfall(code):
    return {
        "Nov": 34.6, "Dec": 20.6, "Jan": 10.0,
        "Feb": 18.0, "Mar": 24.2, "Apr": 50.2, "May": 13.4
    }

rain = get_rainfall(station_code)
st.write(pd.DataFrame.from_dict(rain, orient="index", columns=["Rainfall (mm)"]))

# --- Calculations ---
n_per_tonne = 25.0
adjusted_n = (protein_or_oil / 11.5) * n_per_tonne
n_total_required = yield_t_ha * adjusted_n

soil_n = (nitrate + ammonia) * 4
soil_n += organic_n * 0.03

in_season_n = (n_total_required - soil_n) / nue

# --- Output Summary ---
st.header("📊 Nitrogen Budget Summary")
st.metric("Total N Required (kg/ha)", f"{n_total_required:.1f}")
st.metric("Soil N Contribution (kg/ha)", f"{soil_n:.1f}")
st.metric("In-season N Required (kg/ha)", f"{in_season_n:.1f}")

# --- Footer ---
st.markdown("---")
st.caption("Developed in collaboration with South Coastal Agencies")
