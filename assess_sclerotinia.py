from afren_rules import check_afren_compliance

def assess_sclerotinia_risk(temp, rh, rain, days_since_rain, leaf_wetness_hours,
                             rain_days_last_week, seed_dressed, prior_fungicide_applied,
                             selected_seed_treatment, selected_prior_fungicide, crop_stage):
    score = 0
    if temp >= 13:
        score += 1
    if temp >= 16:
        score += 1
    if rh >= 80:
        score += 1
    if rh >= 90:
        score += 1
    if rain >= 5:
        score += 1
    if rain >= 10:
        score += 1
    if days_since_rain <= 2:
        score += 1
    elif days_since_rain <= 5:
        score += 0.5
    if leaf_wetness_hours >= 24:
        score += 1
    if rain_days_last_week >= 3:
        score += 1
    if seed_dressed and selected_seed_treatment.lower() not in ["saltro", "ilevo"]:
        score -= 0.5
    if prior_fungicide_applied and selected_prior_fungicide.lower() in ["prosaro", "aviator xpro", "miravis star"]:
        score -= 1
    if crop_stage in ["50% Flower", "Petal Drop"]:
        score += 1

    if score >= 5:
        risk = "High"
        reco = "Spray Immediately"
    elif score >= 3:
        risk = "Moderate"
        reco = "Consider a Spray Soon"
    else:
        risk = "Low"
        reco = "Continue to Monitor"

    fungicide_options = [
        {"name": "Prosaro", "group": "3 (DMI)", "persistence": "Moderate"},
        {"name": "Miravis Star", "group": "3+7 (DMI+SDHI)", "persistence": "High"},
        {"name": "Aviator Xpro", "group": "3+11 (DMI+QoI)", "persistence": "Moderate"}
    ]

    return {
        "risk_level": risk,
        "recommendation": reco,
        "warnings": [],
        "fungicide_options": fungicide_options
    }


def assess_septoria_risk(temp, rh, rainfall, crop_stage, has_resistance,
                          seed_dressed, prior_fungicide_applied,
                          selected_seed_treatment, selected_prior_fungicide):
    """
    AFREN-aligned Septoria risk assessment for cereals.
    Integrates MoA and spray count compliance.
    """
    score = 0

    # Basic Septoria risk scoring
    if rh >= 80 and temp >= 15:
        score += 2
    elif rh >= 70:
        score += 1

    if rainfall > 5:
        score += 2

    if "Z30" in crop_stage or "Z39" in crop_stage:
        score += 2

    if not has_resistance:
        score += 1

    # Risk rating
    if score >= 6:
        level = "High"
        recommendation = "Spray immediately with a registered fungicide."
    elif score >= 4:
        level = "Moderate"
        recommendation = "Monitor closely and consider spraying if conditions persist."
    else:
        level = "Low"
        recommendation = "Low risk. Reassess later."

    # Fungicide options
    all_options = [
        {"name": "Prosaro", "group": "3 (DMI)", "persistence": "Moderate"},
        {"name": "Elatus Ace", "group": "3+7 (DMI+SDHI)", "persistence": "High"},
        {"name": "Aviator Xpro", "group": "3+11 (DMI+QoI)", "persistence": "Moderate"},
    ]

    # MoA use tracking
    sdhis_used = any("sdhi" in s.lower() or "group 7" in s.lower()
                     for s in [selected_seed_treatment, selected_prior_fungicide])
    group_3_used = any("group 3" in s.lower() or "dmi" in s.lower()
                       for s in [selected_seed_treatment, selected_prior_fungicide])
    group_11_used = any("group 11" in s.lower() or "qoi" in s.lower()
                        for s in [selected_seed_treatment, selected_prior_fungicide])

    # AFREN warnings
    warnings = check_afren_compliance(
        crop="Wheat",
        disease="septoria",
        total_sprays=2 if prior_fungicide_applied else 1,
        sdhis_used=sdhis_used,
        previous_moa=selected_prior_fungicide,
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

    # Filter options if SDHI already used
    filtered_options = [f for f in all_options if not (sdhis_used and "SDHI" in f["group"])]

    return {
        "risk_level": level,
        "recommendation": recommendation,
        "fungicide_options": filtered_options,
        "warnings": warnings
    }
