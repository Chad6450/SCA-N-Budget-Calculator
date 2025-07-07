import streamlit as st
from PIL import Image

# Page config
st.set_page_config(
    page_title="SCA Agronomy Tools",
    page_icon="🌱",
    layout="centered"
)

# Logo
st.image("sca_logo.jpg", use_container_width=True)

# Center content
with st.container():
    st.markdown("""
        <div style='text-align: center;'>
            <h1>🧮 Agronomy Decision Tools</h1>
            <p>Welcome to the South Coastal Agencies Agronomy Toolkit. Choose a calculator below:</p>
        </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="large")

    with col1:
        if st.button("🌾 Nitrogen Budget Calculator"):
            st.switch_page("pages/Nitrogen_Budget.py")

        if st.button("🦠 Fungicide Risk & ROI Tool"):
            st.switch_page("pages/streamlit_disease_tool.py")  # ✅ Adjust path if needed

    with col2:
        st.button("🧪 More Tools Coming Soon")

st.markdown("---")
st.caption("Developed by South Coastal Agencies")
