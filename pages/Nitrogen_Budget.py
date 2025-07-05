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
st.header("3. Rainfall ")
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

in_season_n = max((n_total_required - soil_n) / nue, 0)

# --- Output Summary ---
st.header("📊 Nitrogen Budget Summary")
st.metric("Total N Required (kg/ha)", f"{n_total_required:.1f}")
st.metric("Soil N Contribution (kg/ha)", f"{soil_n:.1f}")
st.metric("In-season N Required (kg/ha)", f"{in_season_n:.1f}")

# --- ROI & Break-Even Calculator ---
st.header("💰 Return on Investment")

grain_price = st.number_input("Grain Price ($/t)", min_value=0.0, value=400.0, step=10.0)
urea_price = st.number_input("Urea Price ($/t)", min_value=0.0, value=950.0, step=10.0)
uan_price = st.number_input("UAN Price ($/t)", min_value=0.0, value=600.0, step=10.0)

# Cost per kg N
urea_n_cost = urea_price / 460  # 46% N
uan_n_cost = uan_price / 320    # 32% N

# Total cost
urea_total_cost = in_season_n * urea_n_cost
uan_total_cost = in_season_n * uan_n_cost

# Break-even kg grain/ha
grain_price_per_kg = grain_price / 1000
urea_break_even_kg = urea_total_cost / grain_price_per_kg
uan_break_even_kg = uan_total_cost / grain_price_per_kg

# --- ROI Output ---
st.subheader("📈 ROI Comparison")
col5, col6 = st.columns(2)
with col5:
    st.metric("Urea N Cost ($/kg N)", f"${urea_n_cost:.2f}")
    st.metric("Urea Total Cost ($/ha)", f"${urea_total_cost:.2f}")
    st.metric("Urea Break-even Yield (kg/ha)", f"{urea_break_even_kg:.0f}")
with col6:
    st.metric("UAN N Cost ($/kg N)", f"${uan_n_cost:.2f}")
    st.metric("UAN Total Cost ($/ha)", f"${uan_total_cost:.2f}")
    st.metric("UAN Break-even Yield (kg/ha)", f"{uan_break_even_kg:.0f}")

# --- Footer ---
st.markdown("---")
st.caption("Developed in collaboration with South Coastal Agencies")
