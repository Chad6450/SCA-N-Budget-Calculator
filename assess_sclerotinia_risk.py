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
    return {
        "risk_level": risk,
        "recommendation": reco,
        "fungicide_options": [
            {"name": "Prosaro", "group": "3 (DMI)", "persistence": "Moderate"},
            {"name": "Miravis Star", "group": "3+7 (DMI+SDHI)", "persistence": "High"},
            {"name": "Aviator Xpro", "group": "3+11 (DMI+QoI)", "persistence": "Moderate"}
        ]
    }

def assess_septoria_risk(temp, rh, rain, days_since_rain, leaf_wetness_hours,
                          rain_days_last_week, seed_dressed, prior_fungicide_applied,
                          selected_seed_treatment, selected_prior_fungicide, crop_stage):
    score = 0
    if rain_days_last_week >= 3:
        score += 2
    elif rain_days_last_week == 2:
        score += 1
    if temp >= 7:
        score += 1
    if leaf_wetness_hours >= 20:
        score += 2
    if not seed_dressed:
        score += 0.5
    if not prior_fungicide_applied:
        score += 0.5
    if score >= 4:
        risk = "High"
        reco = "Spray Immediately"
    elif score >= 2:
        risk = "Moderate"
        reco = "Consider a Spray Soon"
    else:
        risk = "Low"
        reco = "Continue to Monitor"
    return {
        "risk_level": risk,
        "recommendation": reco,
        "fungicide_options": [
            {"name": "Radial", "group": "3+11", "persistence": "High"},
            {"name": "Opus", "group": "3 (DMI)", "persistence": "Moderate"}
        ]
    }

def assess_rust_risk(temp, rh, crop_stage, has_resistance,
                     seed_dressed, prior_fungicide_applied,
                     selected_seed_treatment, selected_prior_fungicide):
    score = 0
    if 10 <= temp <= 25:
        score += 2
    if rh >= 70:
        score += 1
    if any(stage in crop_stage.lower() for stage in ["flag", "boot", "flower"]):
        score += 1
    if not has_resistance:
        score += 1
    if not seed_dressed:
        score += 0.5
    if not prior_fungicide_applied:
        score += 0.5
    if score >= 4:
        risk = "High"
        reco = "Spray Immediately"
    elif score >= 2:
        risk = "Moderate"
        reco = "Consider a Spray Soon"
    else:
        risk = "Low"
        reco = "Continue to Monitor"
    return {
        "risk_level": risk,
        "recommendation": reco,
        "fungicide_options": [
            {"name": "Tilt", "group": "3 (DMI)", "persistence": "Low"},
            {"name": "Trivapro", "group": "3+7+11", "persistence": "High"}
        ]
    }
