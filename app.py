# -*- coding: utf-8 -*-
import streamlit as st

# Page configuration
st.set_page_config(
    page_title="SCA Agronomy Tools",
    page_icon="🌱",
    layout="centered",
)

# Logo
st.image("sca_logo.jpg", use_container_width=True)

# Custom CSS styling
st.markdown("""
<style>
.tile-container {
    display: flex;
    justify-content: center;
    gap: 30px;
    margin-top: 40px;
    flex-wrap: wrap;
}
.tile-button {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    width: 160px;
    height: 160px;
    background-color: #E0F7FA;
    color: #004D40;
    text-align: center;
    border: 2px solid #00897B;
    border-radius: 20px;
    font-size: 18px;
    font-weight: 600;
    text-decoration: none;
    transition: all 0.2s ease;
}
.tile-button:hover {
    background-color: #B2EBF2;
    border-color: #00796B;
    color: #00332E;
}
.tile-emoji {
    font-size: 40px;
    margin-bottom: 10px;
}
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div style='text-align: center;'>
    <h1>🧮 Agronomy Decision Tools</h1>
    <p>Welcome to the South Coastal Agencies Agronomy Toolkit.</p>
</div>
""", unsafe_allow_html=True)

# Tool tiles using Streamlit's built-in navigation
st.markdown("### 🚀 Choose a Tool:")

col1, col2 = st.columns(2)

with col1:
    st.page_link("pages/nitrogen_budget.py", label="🌾 Nitrogen Budget")

with col2:
   st.page_link("pages/fungicide_decision_tool.py", label="🦠 Fungicide Tool")

# Footer
st.markdown("---")
st.caption("Developed by South Coastal Agencies")
