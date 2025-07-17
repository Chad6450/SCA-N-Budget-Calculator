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
/* App background */
body {
    background-color: #F0FFF4;
}

/* Center container and tile layout */
.tile-container {
    display: flex;
    justify-content: center;
    gap: 30px;
    margin-top: 40px;
    flex-wrap: wrap;
}

/* Tile button styling */
.tile-button {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    width: 160px;
    height: 160px;
    background-color: #ffffff; /* White buttons */
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
    background-color: #e6fff2;
    border-color: #00796B;
    color: #00332E;
}
.tile-button img {
    width: 50px;
    height: 50px;
    margin-bottom: 10px;
}
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div style='text-align: center;'>
    <h1>Agronomy Decision Tools</h1>
    <p>Welcome to the South Coastal Agencies Agronomy Toolkit.</p>
</div>
""", unsafe_allow_html=True)

# Tile buttons
st.markdown("""
<div class="tile-container">
    <a href="/pages/nitrogen_budget" class="tile-button">
        <img src="https://raw.githubusercontent.com/Chad6450/SCA-N-Budget-Calculator/main/home_icon.png" alt="Nitrogen Icon" />
        Nitrogen Budget
    </a>
    <a href="/pages/fungicide_decision_tool" class="tile-button">
        <img src="https://raw.githubusercontent.com/Chad6450/SCA-N-Budget-Calculator/main/dollar_leaf.png" alt="Fungicide Icon" />
        Fungicide Tool
    </a>
</div>
""", unsafe_allow_html=True)

# Footer
st.markdown("---")
st.caption("Developed by South Coastal Agencies")