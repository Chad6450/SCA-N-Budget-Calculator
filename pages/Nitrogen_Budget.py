import streamlit as st
import pandas as pd
from fpdf import FPDF
import base64
from io import BytesIO
import matplotlib.pyplot as plt
import os

# --- Branding ---
st.image("sca_logo.jpg", width=150)  # Make logo larger
st.markdown("### Nitrogen Budget Calculator – South Coastal Agencies")

# --- Agronomic Inputs ---
st.markdown("---")  # Reduced spacing above this header
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
st.header("\U0001F4CA Nitrogen Budget Summary")
st.metric("Total N Required (kg/ha)", f"{n_total_required:.1f}")
st.metric("Soil N Contribution (kg/ha)", f"{soil_n:.1f}")
st.metric("In-season N Required (kg/ha)", f"{in_season_n:.1f}")

# --- ROI & Break-Even Calculator ---
st.header("\U0001F4B0 Return on Investment")

grain_price = st.number_input("Grain Price ($/t)", min_value=0.0, value=400.0, step=10.0)
urea_price = st.number_input("Urea Price ($/t)", min_value=0.0, value=950.0, step=10.0)
uan_price = st.number_input("UAN Price ($/t)", min_value=0.0, value=600.0, step=10.0)

# Cost per kg N
urea_n_cost = urea_price / 460  # 46% N
uan_n_cost = uan_price / 320    # 32% N

# Total cost
urea_total_cost = in_season_n * urea_n_cost
uan_total_cost = in_season_n * uan_n_cost

grain_price_per_kg = grain_price / 1000
urea_break_even_kg = urea_total_cost / grain_price_per_kg
uan_break_even_kg = uan_total_cost / grain_price_per_kg

# --- ROI Output ---
st.subheader("\U0001F4C8 ROI Comparison")
col5, col6 = st.columns(2)
with col5:
    st.metric("Urea N Cost ($/kg N)", f"${urea_n_cost:.2f}")
    st.metric("Urea Total Cost ($/ha)", f"${urea_total_cost:.2f}")
    st.metric("Urea Break-even Yield (kg/ha)", f"{urea_break_even_kg:.0f}")
with col6:
    st.metric("UAN N Cost ($/kg N)", f"${uan_n_cost:.2f}")
    st.metric("UAN Total Cost ($/ha)", f"${uan_total_cost:.2f}")
    st.metric("UAN Break-even Yield (kg/ha)", f"{uan_break_even_kg:.0f}")

# --- PDF Export ---
class PDF(FPDF):
    def header(self):
        self.image("sca_logo.jpg", x=70, y=8, w=70)  # Bigger and centered
        self.set_font("Arial", 'B', 12)
        self.set_y(35)
        self.cell(0, 10, "Nitrogen Budget Report", ln=True, align='C')
        self.ln(8)

    def chapter_title(self, title):
        self.set_font("Arial", 'B', 10)
        self.cell(0, 10, title, ln=True)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)

    def chapter_body(self, text):
        self.set_font("Arial", '', 10)
        self.multi_cell(0, 8, text)
        self.ln()

    def boxed_text(self, title, content):
        self.set_font("Arial", 'B', 11)
        self.set_fill_color(240, 240, 240)
        y = self.get_y()
        self.rect(10, y, 190, 30)
        self.set_xy(12, y + 2)
        self.multi_cell(0, 8, f"{title}\n{content}")
        self.ln(10)

if st.button("\U0001F4C4 Download PDF Report"):
    pdf = PDF()
    pdf.add_page()

    pdf.chapter_title("1. Yield Expectations")
    pdf.chapter_body(f"Crop Type: {crop_type}\nExpected Yield: {yield_t_ha} t/ha\n{label}: {protein_or_oil}%\nNUE: {nue}")

    pdf.chapter_title("2. Soil Test Data")
    pdf.chapter_body(f"Nitrate: {nitrate} mg/kg\nAmmonia: {ammonia} mg/kg\nOrganic N Pool: {organic_n} kg/ha")

    pdf.chapter_title("3. Rainfall")
    pdf.chapter_body(f"Station: {station_code}\nRainfall: {rain}")

    # Create rainfall graph
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
    pdf.image("temp_rain_chart.png", x=50, w=100)  # Smaller and centered

    pdf.add_page()

    pdf.chapter_title("4. Nitrogen Summary")
    pdf.set_font("Arial", 'B', 12)
    pdf.set_fill_color(230, 230, 250)
    pdf.multi_cell(0, 10, f"Total N Required: {n_total_required:.1f} kg/ha\nSoil N Contribution: {soil_n:.1f} kg/ha\nIn-season N Required: {in_season_n:.1f} kg/ha", border=1)
    pdf.ln(5)

    pdf.chapter_title("5. ROI Assumptions & Break-even Analysis")
    pdf.set_font("Arial", 'B', 12)
    pdf.set_fill_color(230, 230, 250)
    pdf.multi_cell(0, 10,
        f"Grain Price: ${grain_price}/t\n"
        f"Urea Price: ${urea_price}/t (46% N)\n"
        f"UAN Price: ${uan_price}/t (32% N)\n\n"
        f"Urea Cost: ${urea_total_cost:.2f}/ha | Break-even Yield: {urea_break_even_kg:.0f} kg/ha\n"
        f"UAN Cost: ${uan_total_cost:.2f}/ha | Break-even Yield: {uan_break_even_kg:.0f} kg/ha",
        border=1
    )

    pdf_data = pdf.output(dest='S').encode('latin1')
    b64 = base64.b64encode(pdf_data).decode()
    href = f'<a href="data:application/pdf;base64,{b64}" target="_blank">\U0001F4C4 View PDF Report in Browser</a>'
    st.markdown(href, unsafe_allow_html=True)

    # Clean up temp chart image
    os.remove("temp_rain_chart.png")

# --- Footer ---
st.markdown("---")
st.caption("Developed in collaboration with South Coastal Agencies")
