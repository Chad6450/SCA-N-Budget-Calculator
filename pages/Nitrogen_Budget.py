import streamlit as st 
import pandas as pd
from fpdf import FPDF
import base64
from io import BytesIO
import matplotlib.pyplot as plt
import os
from datetime import datetime

try:
    import qrcode
    QR_AVAILABLE = True
except ImportError:
    QR_AVAILABLE = False

# --- Helper Function ---
def clean_ascii(text):
    return text.encode('ascii', errors='replace').decode('ascii')

# --- Branding ---
st.image("sca_logo.jpg", use_container_width=True)
st.markdown("<h2 style='color:#1a4d2e;'>🌿 Nitrogen Budget Calculator – South Coastal Agencies</h2>", unsafe_allow_html=True)

# --- Apply Brand Colors in CSS ---
st.markdown("""
    <style>
    /* Global font and color styling */
    .reportview-container .markdown-text-container {
        font-family: 'Arial';
        color: #1a4d2e;
    }

    h1, h2, h3 {
        color: #1a4d2e;
    }

    /* Button styling */
    .stButton>button {
        background-color: #1a4d2e;
        color: white;
        border-radius: 8px;
        padding: 0.5em 1.5em;
        font-weight: 600;
    }

    .stButton>button:hover {
        background-color: #3a7759;
    }

    /* Input field styling */
    input[type="text"], input[type="number"], textarea, .stNumberInput input {
        background-color: #e8f5e9 !important;
        color: #1a4d2e !important;
        border-radius: 6px !important;
    }

    /* Selectbox styling */
    div[data-baseweb="select"] > div {
        background-color: #e8f5e9 !important;
        color: #1a4d2e !important;
        border-radius: 6px !important;
    }

    div[data-baseweb="select"] input {
        color: #1a4d2e !important;
    }

    div[data-baseweb="select"] span {
        color: #1a4d2e !important;
    }

    /* Slider styling */
    .stSlider > div {
        color: #1a4d2e !important;
    }

    /* Card-style section boxes */
    .card {
        background-color: #e8f5e9;
        border-left: 6px solid #1a4d2e;
        padding: 20px;
        margin-bottom: 20px;
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# --- Agronomic Inputs ---
st.markdown("---")
st.header("1. 🌾 Yield Expectations")
crop_type = st.selectbox("Crop Type", ["Wheat", "Barley", "Oats", "Canola"])

if crop_type.lower() == "canola":
    label = "Target Oil (%)"
    default_value = 42.0
    yield_default = 2.0
    grain_price_default = 850.0
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
else:
    label = "Target Protein (%)"
    default_value = 11.5
    yield_default = 4.0
    grain_price_default = 350.0

col1, col2 = st.columns(2)
with col1:
    yield_t_ha = st.number_input("Expected Yield (t/ha)", min_value=0.0, value=yield_default, step=0.1)
with col2:
    protein_or_oil = st.number_input(label, min_value=0.0, value=default_value, step=0.1)

grain_price = st.number_input("Grain Price ($/t)", min_value=0.0, value=grain_price_default, step=10.0)
urea_price = st.number_input("Urea Price ($/t)", min_value=0.0, value=835.0, step=10.0)
uan_price = st.number_input("UAN Price ($/t)", min_value=0.0, value=725.0, step=10.0)

nue = st.slider("Nitrogen Use Efficiency (NUE)", min_value=0.1, max_value=1.0, value=0.6, step=0.05)

# --- Additional Nitrogen Calculations ---
n_per_tonne = 25.0
adjusted_n = (protein_or_oil / 11.5) * n_per_tonne
n_total_required = yield_t_ha * adjusted_n
soil_n = 50.0  # Placeholder for now
in_season_n = max((n_total_required - soil_n) / nue, 0)

urea_cost_per_unit = urea_price / 460
uan_cost_per_unit = uan_price / 320
urea_total_cost = in_season_n * urea_cost_per_unit
uan_total_cost = in_season_n * uan_cost_per_unit
grain_price_per_kg = grain_price / 1000
urea_break_even_kg = urea_total_cost / grain_price_per_kg
uan_break_even_kg = uan_total_cost / grain_price_per_kg

roi = clean_ascii(
    f"Grain Price: ${grain_price:.2f}/t\n"
    f"Urea Price: ${urea_price:.2f}/t (46% N)\n"
    f"UAN Price: ${uan_price:.2f}/t (32% N)\n"
    f"\nUrea Cost: ${urea_total_cost:.2f}/ha\n"
    f"Urea N Cost: ${urea_cost_per_unit:.2f}/kg N\n"
    f"Urea Break-even: {urea_break_even_kg:.0f} kg/ha\n"
    f"\nUAN Cost: ${uan_total_cost:.2f}/ha\n"
    f"UAN N Cost: ${uan_cost_per_unit:.2f}/kg N\n"
    f"UAN Break-even: {uan_break_even_kg:.0f} kg/ha"
)
# --- Soil Test Inputs ---
st.header("2. 📉 Soil Test Data")
col3, col4 = st.columns(2)
with col3:
    nitrate = st.number_input("Nitrate-N (mg/kg)", min_value=0.0, value=5.0)
with col4:
    ammonia = st.number_input("Ammonia-N (mg/kg)", min_value=0.0, value=2.0)

organic_n = st.number_input("Organic N Pool (kg/ha)", min_value=0.0, value=1560.0)

# --- Legume Contribution ---
st.header("3. 🌱 Previous Legume Crop")
had_legume = st.radio("Was there a legume crop last year?", ["No", "Yes"])
legume_n = 0.0
legume_biomass = 0.0
if had_legume == "Yes":
    legume_biomass = st.number_input("Legume Biomass (t/ha)", min_value=0.0, value=2.0, step=0.1)
    legume_n = legume_biomass * 20.0

# --- Rainfall Data Input ---
st.header("4. ☔️ Rainfall")
rainfall_input_mode = st.radio("Rainfall Data Input Mode", ["Use DPIRD API", "Enter Manually"])

if rainfall_input_mode == "Use DPIRD API":
    station_code = st.text_input("Enter DPIRD Station Code", value="ESP")
    @st.cache_data
    def get_rainfall(code):
        return {"Jan": 10.0, "Feb": 18.0, "Mar": 24.2, "Apr": 50.2, "May": 13.4,
                "Jun": 40.0, "Jul": 60.0, "Aug": 55.0, "Sep": 45.0, "Oct": 30.0, "Nov": 34.6, "Dec": 20.6}
    rain = get_rainfall(station_code)
    rain_source = f"DPIRD Station Code: {station_code}"
else:
    rain = {}
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    for month in months:
        rain[month] = st.number_input(f"Rainfall for {month} (mm)", min_value=0.0, value=20.0)
    station_code = "Manual Entry"
    rain_source = "Manual rainfall entry"

rain_df = pd.DataFrame.from_dict(rain, orient="index", columns=["Rainfall (mm)"]).sort_index()
st.write(rain_df)

# --- Calculations ---
n_per_tonne = 25.0
adjusted_n = (protein_or_oil / 11.5) * n_per_tonne
n_total_required = yield_t_ha * adjusted_n

soil_n = (nitrate + ammonia) * 4
soil_n += organic_n * 0.03
soil_n += legume_n

in_season_n = max((n_total_required - soil_n) / nue, 0)

# --- Output Summary ---
st.header("📊 Nitrogen Budget Summary")
st.metric("Total N Required (kg/ha)", f"{n_total_required:.1f}")
st.metric("Soil N Contribution incl. legume (kg/ha)", f"{soil_n:.1f}")
st.metric("In-season N Required (kg/ha)", f"{in_season_n:.1f}")

st.markdown("---")
st.header("📄 Nitrogen Product Cost & Break-even Summary")

col_a, col_b = st.columns(2)

with col_a:
    st.subheader("Urea")
    st.markdown(f"**N Cost:** ${urea_cost_per_unit:.2f}/kg N")
    st.markdown(f"**Total Cost/ha:** ${urea_total_cost:.2f}")
    st.markdown(f"**Break-even Yield:** {urea_break_even_kg:.0f} kg/ha")

with col_b:
    st.subheader("UAN")
    st.markdown(f"**N Cost:** ${uan_cost_per_unit:.2f}/kg N")
    st.markdown(f"**Total Cost/ha:** ${uan_total_cost:.2f}")
    st.markdown(f"**Break-even Yield:** {uan_break_even_kg:.0f} kg/ha")

# --- PDF Export ---
class PDF(FPDF):
    def header(self):
        self.image("sca_logo.jpg", x=10, w=190)
        self.ln(28)
        self.set_font("Arial", 'B', 16)
        self.cell(0, 10, "Nitrogen Budget Report", ln=True, align='C')
        self.ln(8)

    def summary_side_by_side(self, rainfall_chart, yield_text, soil_text, rain_data, summary_text, roi_text, qr_path):
        self.set_font("Arial", '', 10)
        y_start = self.get_y()

        self.set_xy(10, y_start)
        rain_text = "\n".join([f"{month}: {val} mm" for month, val in rain_data.items()])
        left_content = (
            f"Yield Expectations\n{yield_text}\n\n"
            f"Soil Test Data\n{soil_text}\n\n"
            f"Rainfall\n{rain_source}\n{rain_text}"
        )
        self.multi_cell(90, 6, left_content)
        self.image(rainfall_chart, x=10, y=self.get_y(), w=90)

        x_right = 110
        self.set_xy(x_right, y_start)
        self.set_font("Arial", 'B', 10)
        self.set_x(x_right)
        self.cell(0, 6, "Nitrogen Summary", ln=True)
        self.set_font("Arial", '', 10)
        self.set_x(x_right)
        self.multi_cell(85, 6, summary_text)
        self.ln(3)

        self.set_font("Arial", 'B', 10)
        self.set_x(x_right)
        self.cell(0, 6, "ROI & Break-even Analysis", ln=True)
        self.set_font("Arial", '', 10)
        self.set_x(x_right)
        self.multi_cell(85, 6, roi_text)
        if QR_AVAILABLE:
            self.image(qr_path, x=165, y=260, w=30)

if st.button("📄 Download PDF Report"):
    pdf = PDF()
    pdf.add_page()

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

    qr_path = "temp_qr_code.png"
    if QR_AVAILABLE:
        qr = qrcode.make("https://sca.agtools.app")
        qr.save(qr_path)

    yield_info = clean_ascii(
        f"Crop Type: {crop_type}\nExpected Yield: {yield_t_ha:.1f} t/ha\n{label}: {protein_or_oil}%\nNUE: {nue}"
    )
    soil_info = clean_ascii(
        f"Nitrate: {nitrate} mg/kg\nAmmonia: {ammonia} mg/kg\nOrganic N Pool: {organic_n:.1f} kg/ha\nLegume N Credit: {legume_n:.1f} kg/ha ({legume_biomass:.1f} t/ha biomass)"
    )
    summary = clean_ascii(
        f"Total N Required: {n_total_required:.1f} kg/ha\nSoil N Contribution: {soil_n:.1f} kg/ha\nIn-season N Required: {in_season_n:.1f} kg/ha"
    )
    roi = clean_ascii(
        f"Grain Price: ${grain_price_default}/t\nUrea Price: $835/t (46% N)\nUAN Price: $715/t (32% N)\n\nUrea Cost: ${(in_season_n * (835 / 460)):.2f}/ha\nBreak-even: {(in_season_n * (835 / 460)) / (grain_price_default / 1000):.0f} kg/ha\nUAN Cost: ${(in_season_n * (715 / 320)):.2f}/ha\nBreak-even: {(in_season_n * (715 / 320)) / (grain_price_default / 1000):.0f} kg/ha"
    )

    pdf.summary_side_by_side("temp_rain_chart.png", yield_info, soil_info, rain, summary, roi, qr_path if QR_AVAILABLE else None)

    pdf_data = pdf.output(dest='S').encode('latin-1', errors='replace')
    b64 = base64.b64encode(pdf_data).decode()
    href = f'<a href="data:application/pdf;base64,{b64}" target="_blank">📥 Click here to download PDF</a>'
    st.markdown(href, unsafe_allow_html=True)

    os.remove("temp_rain_chart.png")
    if QR_AVAILABLE:
        os.remove(qr_path)

# --- Footer ---
st.markdown("---")
st.caption("Developed in collaboration with South Coastal Agencies")