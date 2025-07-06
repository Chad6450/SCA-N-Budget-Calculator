import streamlit as st
import pandas as pd
from fpdf import FPDF
import base64
from io import BytesIO
import matplotlib.pyplot as plt
import os
import qrcode

# --- Helper Function ---
def clean_ascii(text):
    return text.encode('ascii', errors='replace').decode('ascii')

# --- Branding ---
st.image("sca_logo.jpg", use_container_width=True)
st.markdown("### Nitrogen Budget Calculator – South Coastal Agencies")

# --- Agronomic Inputs ---
st.markdown("---")
st.header("1. Yield Expectations")
crop_type = st.selectbox("Crop Type", ["Wheat", "Barley", "Oats", "Canola"])

# Set label and default values based on crop type
if crop_type.lower() == "canola":
    label = "Target Oil (%)"
    default_value = 42.0
    yield_default = 2.0
    grain_price_default = 800.0
elif crop_type.lower() == "barley":
    label = "Target Protein (%)"
    default_value = 11.5
    yield_default = 4.0
    grain_price_default = 330.0
elif crop_type.lower() == "oats":
    label = "Target Protein (%)"
    default_value = 11.5
    yield_default = 4.0
    grain_price_default = 280.0
else:  # Wheat
    label = "Target Protein (%)"
    default_value = 11.5
    yield_default = 4.0
    grain_price_default = 350.0

col1, col2 = st.columns(2)
with col1:
    yield_t_ha = st.number_input("Expected Yield (t/ha)", min_value=0.0, value=yield_default, step=0.1)
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
rain_df = pd.DataFrame.from_dict(rain, orient="index", columns=["Rainfall (mm)"]).sort_index()
st.write(rain_df)

# --- Calculations ---
n_per_tonne = 25.0
adjusted_n = (protein_or_oil / 11.5) * n_per_tonne
n_total_required = yield_t_ha * adjusted_n

soil_n = (nitrate + ammonia) * 4
soil_n += organic_n * 0.03

in_season_n = max((n_total_required - soil_n) / nue, 0)

# --- Output Summary ---
st.header("Nitrogen Budget Summary")
st.metric("Total N Required (kg/ha)", f"{n_total_required:.1f}")
st.metric("Soil N Contribution (kg/ha)", f"{soil_n:.1f}")
st.metric("In-season N Required (kg/ha)", f"{in_season_n:.1f}")

# --- ROI & Break-Even Calculator ---
st.header("Return on Investment")

grain_price = st.number_input("Grain Price ($/t)", min_value=0.0, value=grain_price_default, step=10.0)
urea_price = st.number_input("Urea Price ($/t)", min_value=0.0, value=835.0, step=10.0)
uan_price = st.number_input("UAN Price ($/t)", min_value=0.0, value=715.0, step=10.0)

# Cost per kg N
urea_n_cost = urea_price / 460
uan_n_cost = uan_price / 320

# Total cost
urea_total_cost = in_season_n * urea_n_cost
uan_total_cost = in_season_n * uan_n_cost

grain_price_per_kg = grain_price / 1000
urea_break_even_kg = urea_total_cost / grain_price_per_kg
uan_break_even_kg = uan_total_cost / grain_price_per_kg

# --- ROI Output ---
st.subheader("ROI Comparison")
col5, col6 = st.columns(2)

with col5:
    st.markdown("### Urea")
    st.metric("N Cost ($/kg N)", f"${urea_n_cost:.2f}")
    st.metric("Total Cost ($/ha)", f"${urea_total_cost:.2f}")
    st.metric("Break-even Yield (kg/ha)", f"{urea_break_even_kg:.0f}")

with col6:
    st.markdown("### UAN")
    st.metric("N Cost ($/kg N)", f"${uan_n_cost:.2f}")
    st.metric("Total Cost ($/ha)", f"${uan_total_cost:.2f}")
    st.metric("Break-even Yield (kg/ha)", f"{uan_break_even_kg:.0f}")

# --- PDF Export ---
class PDF(FPDF):
    def header(self):
        self.image("sca_logo.jpg", x=10, w=190)
        self.ln(22)
        self.set_font("Arial", 'B', 12)
        self.cell(0, 10, "Nitrogen Budget Report", ln=True, align='C')
        self.ln(4)

    def summary_side_by_side(self, rainfall_chart, yield_text, soil_text, rain_data, summary_text, roi_text, qr_path):
        self.set_font("Arial", '', 10)
        green_fill = (163, 198, 140)
        y_start = self.get_y()
        self.set_xy(10, y_start)

        rain_text = "\n".join([f"{month}: {val} mm" for month, val in rain_data.items()])
        self.multi_cell(90, 6, f"Yield Expectations\n{yield_text}\n\nSoil Test Data\n{soil_text}\n\nRainfall\nStation: {station_code}\n{rain_text}")
        self.image(rainfall_chart, x=10, y=self.get_y(), w=90)

        self.set_xy(105, y_start)
        self.set_fill_color(*green_fill)
        self.set_font("Arial", 'B', 10)
        self.multi_cell(95, 6, "Nitrogen Summary", border='B')
        self.set_font("Arial", '', 10)
        self.multi_cell(95, 6, summary_text, border=1, fill=True)
        self.ln(3)
        self.set_font("Arial", 'B', 10)
        self.multi_cell(95, 6, "ROI & Break-even Analysis", border='B')
        self.set_font("Arial", '', 10)
        self.multi_cell(95, 6, roi_text, border=1, fill=True)
        self.image(qr_path, x=165, y=260, w=30)

if st.button("Download PDF Report"):
    pdf = PDF()
    pdf.add_page()

    # Rainfall graph
    plt.figure(figsize=(3.5, 1.5))
    plt.bar(rain_df.index, rain_df["Rainfall (mm)"])
    plt.title(f"Rainfall at {station_code}", fontsize=9)
    plt.ylabel("mm", fontsize=8)
    plt.xticks(fontsize=8)
    plt.yticks(fontsize=8)
    plt.tight_layout()
    img_buffer = BytesIO()
    plt.savefig(img_buffer, format='png')
    img_buffer.seek(0)
    with open("temp_rain_chart.png", "wb") as f:
        f.write(img_buffer.read())
    plt.close()

    # QR Code
    qr = qrcode.make("https://sca.agtools.app")
    qr_path = "temp_qr_code.png"
    qr.save(qr_path)

    yield_info = clean_ascii(
        f"Crop Type: {crop_type}\n"
        f"Expected Yield: {yield_t_ha:.1f} t/ha\n"
        f"{label}: {protein_or_oil}%\n"
        f"NUE: {nue}"
    )
    soil_info = clean_ascii(
        f"Nitrate: {nitrate} mg/kg\n"
        f"Ammonia: {ammonia} mg/kg\n"
        f"Organic N Pool: {organic_n:.1f} kg/ha"
    )
    summary = clean_ascii(
        f"Total N Required: {n_total_required:.1f} kg/ha\n"
        f"Soil N Contribution: {soil_n:.1f} kg/ha\n"
        f"In-season N Required: {in_season_n:.1f} kg/ha"
    )
    roi = clean_ascii(
        f"Grain Price: ${grain_price}/t\n"
        f"Urea Price: ${urea_price}/t (46% N)\n"
        f"UAN Price: ${uan_price}/t (32% N)\n"
        f"\nUrea Cost: ${urea_total_cost:.2f}/ha\nBreak-even: {urea_break_even_kg:.0f} kg/ha\n"
        f"UAN Cost: ${uan_total_cost:.2f}/ha\nBreak-even: {uan_break_even_kg:.0f} kg/ha"
    )
    pdf.summary_side_by_side("temp_rain_chart.png", yield_info, soil_info, rain, summary, roi, qr_path)

    pdf_data = pdf.output(dest='S').encode('latin-1', errors='replace')
    b64 = base64.b64encode(pdf_data).decode()
    href = f'<a href="data:application/pdf;base64,{b64}" target="_blank">View PDF Report in Browser</a>'
    st.markdown(href, unsafe_allow_html=True)

    os.remove("temp_rain_chart.png")
    os.remove(qr_path)

# --- Footer ---
st.markdown("---")
st.caption("Developed in collaboration with South Coastal Agencies")
