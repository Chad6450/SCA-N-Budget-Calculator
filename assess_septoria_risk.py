from afren_rules import check_afren_compliance

def assess_septoria_risk(temp, rh, rain, days_since_rain, leaf_wetness_hours,
                          rain_days_last_week, seed_dressed, prior_fungicide,
                          seed_treatment_name, prior_fungicide_name, crop_stage):
    """
    AFREN-aligned Septoria tritici blotch risk assessment for wheat.
    Applies weather-based risk logic and AFREN compliance filtering.
    """
    risk_score = 0

    # --- Risk scoring (weather & stage) ---
    if rh >= 80:
        risk_score += 2
    elif rh >= 70:
        risk_score += 1

    if rain >= 50:
        risk_score += 2
    elif rain >= 30:
        risk_score += 1

    if leaf_wetness_hours > 40:
        risk_score += 2
    elif leaf_wetness_hours > 20:
        risk_score += 1

    if days_since_rain <= 3:
        risk_score += 1

    if "Z39" in crop_stage or "Z49" in crop_stage:
        risk_score += 2
    elif "Z30" in crop_stage or "Z31" in crop_stage:
        risk_score += 1

    if prior_fungicide and prior_fungicide_name != "None":
        risk_score -= 1
    if seed_dressed and seed_treatment_name != "None":
        risk_score -= 1

    # --- Risk classification ---
    if risk_score >= 6:
        risk_level = "High"
        recommendation = "Spray immediately with an effective foliar fungicide."
    elif risk_score >= 4:
        risk_level = "Moderate"
        recommendation = "Monitor and consider fungicide if wet conditions persist."
    else:
        risk_level = "Low"
        recommendation = "Monitor. No immediate action required."

    # --- Fungicide options (pre-filtered list) ---
    all_options = [
        {"name": "Prosaro", "group": "Group 3 - DMI", "persistence": "10–14 days"},
        {"name": "Opera", "group": "Group 11+3 - QoI+DMI", "persistence": "12–18 days"}
    ]

    # --- MoA detection ---
    sdhis_used = any(k in s for k in ["SDHI", "Group 7"] for s in [seed_treatment_name, prior_fungicide_name])
    group_3_used = any("Group 3" in s or "DMI" in s for s in [seed_treatment_name, prior_fungicide_name])
    group_11_used = any("Group 11" in s or "QoI" in s for s in [seed_treatment_name, prior_fungicide_name])

    # --- AFREN check ---
    warnings = check_afren_compliance(
        crop="Wheat",
        disease="yellow_spot",
        total_sprays=2 if prior_fungicide_name != "None" else 1,
        sdhis_used=sdhis_used,
        previous_moa=prior_fungicide_name,
        current_moa=" + ".join(set(f["group"] for f in all_options)),
        total_group_3_sprays=1 if group_3_used else 0,
        total_group_7_sprays=1 if sdhis_used else 0,
        total_group_11_sprays=1 if group_11_used else 0,
        blackleg_group_same_as_last_year=False,
        same_crop_last_2_years=False,
        variety_resistance_rating="moderate",
        disease_visible=False,
        fungicide_type="foliar",
        rain_forecast_hours=0
    )

    # --- Filter out MoA conflicts ---
    filtered_options = all_options
    if sdhis_used:
        filtered_options = [f for f in filtered_options if "Group 7" not in f["group"] and "SDHI" not in f["group"]]
    if group_11_used:
        filtered_options = [f for f in filtered_options if "Group 11" not in f["group"] and "QoI" not in f["group"]]

    return {
        "risk_level": risk_level,
        "recommendation": recommendation,
        "fungicide_options": filtered_options,
        "warnings": warnings
    }
