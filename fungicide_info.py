
import streamlit as st

def display_fungicide_info(crop_type, disease_type):
    st.subheader("🧪 Fungicide Guidance")

    if crop_type == "Canola":
        st.markdown("**Fungicide Types to Consider for Blackleg:**")
        st.write("- Group D (Fluquinconazole): Early systemic protection, moderate residual")
        st.write("- Group 3 (Tebuconazole, Prothioconazole): Strong activity, moderate residual")
        st.write("- Group 7 (SDHI – Bixafen): Longer residual, useful under high disease pressure")

    elif crop_type == "Wheat":
        st.markdown("**Fungicide Types to Consider for Yellow Spot:**")
        st.write("- Group 3 (Tebuconazole): Effective but short-lived")
        st.write("- Group 11 (Strobilurin – Azoxystrobin): Good persistence, apply preventatively")
        st.write("- Group 7 (SDHI): Longer protection when used in mixtures")

    elif crop_type == "Barley":
        st.markdown("**Fungicide Types to Consider for Rust:**")
        st.write("- Group 3 (Epoxiconazole, Tebuconazole): Fast knockdown, moderate duration")
        st.write("- Group 11 (Pyraclostrobin): Broad-spectrum, good residual")
        st.write("- Group 7 (Fluxapyroxad): High persistence, effective under heavy pressure")

    st.markdown("**Application Tips:**")
    st.write("- Apply early in crop development if disease pressure or risk is high.")
    st.write("- Tank mix across fungicide groups to reduce resistance risk.")
    st.write("- Consider withholding period and economic return.")
