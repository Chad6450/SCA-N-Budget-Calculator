from afren_rules import check_afren_compliance

def assess_rust_risk(temp, rh, crop_stage, has_resistance,
                      seed_dressed, prior_fungicide,
                      seed_treatment_name, prior_fungicide_name):
    """
    AFREN-aligned rust risk assessment (stripe, stem, or leaf rust) for cereals.
    Integrates AFREN compliance checks for MoA and spray count.
    """
    risk_score = 0

    # --- AFREN-aligned thresholds ---
    if 15 <= temp <= 25:
        risk_score += 2
    elif 12 <= temp < 15 or 25 < temp <= 30:
        risk_score += 1

    if rh >= 85:
        risk_score += 2
    elif rh >= 70:
        risk_score += 1

    if "Z30" in crop_stage or "Z39" in crop_stage or "Z49" in crop_stage or "Z65" in crop_stage:
        risk_score += 2

    if not has_resistance:
        risk_score += 1

    if prior_fungicide and prior_fungicide_name != "None":
        risk_score -= 1
    if seed_dressed and seed_treatment_name != "None":
        risk_score -= 1

    if risk_score >= 6:
        risk_level = "High"
        recommendation = "Apply fungicide immediately."
    elif risk_score >= 4:
        risk_level = "Moderate"
        recommendation = "Monitor closely. Consider fungicide if conditions persist."
    else:
        risk_level = "Low"
        recommendation = "Low risk. Monitor and reassess later."

    all_options = [
        {"name": "Tilt", "group": "Group 3 - DMI", "persistence": "10–14 days"},
        {"name": "Elatus Ace", "group": "Group 7+3 - SDHI+DMI", "persistence": "18–24 days"}
    ]

    # Determine if prior treatment includes SDHI
    sdhis_used = any(keyword in selected for keyword in ["SDHI", "Group 7"]
                     for selected in [seed_treatment_name, prior_fungicide_name])

    previous_moa = prior_fungicide_name
    current_moa = " + ".join(set(f["group"] for f in all_options))

    warnings = check_afren_compliance(
        crop="Wheat",
        disease="rust",
        total_sprays=2 if prior_fungicide_name != "None" else 1,
        sdhis_used=sdhis_used,
        previous_moa=previous_moa,
        current_moa=current_moa,
        total_group_3_sprays=1,
        total_group_7_sprays=1 if sdhis_used else 0,
        total_group_11_sprays=0,
        blackleg_group_same_as_last_year=False,
        same_crop_last_2_years=False,
        variety_resistance_rating="moderate",
        disease_visible=False,
        fungicide_type="foliar",
        rain_forecast_hours=0
    )

    if sdhis_used:
        fungicide_options = [f for f in all_options if "SDHI" not in f["group"] and "Group 7" not in f["group"]]
    else:
        fungicide_options = all_options

    return {
        "risk_level": risk_level,
        "recommendation": recommendation,
        "fungicide_options": fungicide_options,
        "warnings": warnings
    }