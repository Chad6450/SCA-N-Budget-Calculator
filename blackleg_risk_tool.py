from afren_rules import check_afren_compliance

def evaluate_blackleg_risk(inputs):
    variety_resistance_ratings = {
        "43Y92CL": {"blackleg_rating": "R", "group": "ABC"},
        "44Y94CL": {"blackleg_rating": "MR", "group": "ABD"},
        "HyTTec Trident": {"blackleg_rating": "MRMS", "group": "ACD"},
        "4540P": {"blackleg_rating": "R", "group": "ACD"},
        "4520P": {"blackleg_rating": "R", "group": "ABD"},
        "Hunter": {"blackleg_rating": "MR", "group": "AC"},
        "Emu": {"blackleg_rating": "MR", "group": "AD"},
        "Py525g": {"blackleg_rating": "MR", "group": "BCD"},
        "DG Buller": {"blackleg_rating": "MS", "group": "BD"},
        "Other": {"blackleg_rating": "MS", "group": "AC"}
    }

    def calculate_spore_risk(rain_mm, rh_percent, temperature_c):
        risk = 0
        if rain_mm >= 2:
            risk += 1
        if rh_percent >= 80:
            risk += 1
        if 10 <= temperature_c <= 20:
            risk += 1
        return "High" if risk >= 2 else "Moderate" if risk == 1 else "Low"

    def calculate_break_even_yield(fungicide_cost, application_cost, grain_price):
        total_cost = fungicide_cost + application_cost
        return round(total_cost / grain_price * 1000, 1)

    variety_info = variety_resistance_ratings.get(inputs["variety"], variety_resistance_ratings["Other"])
    spore_risk = calculate_spore_risk(inputs["rain_mm"], inputs["rh_percent"], inputs["temperature_c"])
    break_even = calculate_break_even_yield(inputs["fungicide_cost"], inputs["application_cost"], inputs["grain_price"])

    blackleg_rating = variety_info.get("blackleg_rating", "Unknown")
    blackleg_group = variety_info.get("group", "Unknown")

    fungicide_options = [
        {"name": "Prosaro", "group": "Group 3 - DMI", "persistence": "Moderate"},
        {"name": "Miravis Star", "group": "Group 3+7 - DMI+SDHI", "persistence": "High"},
        {"name": "Aviator Xpro", "group": "Group 3+11 - DMI+QoI", "persistence": "Moderate"}
    ]

    prior_fungicide = inputs.get("prior_fungicide", "None")
    seed_treatment = inputs.get("seed_treatment", "None")

    sdhis_used = any(moa in s.lower() for moa in ["sdhi", "group 7"] for s in [prior_fungicide, seed_treatment])
    group_3_used = any("group 3" in s.lower() or "dmi" in s.lower() for s in [prior_fungicide, seed_treatment])
    group_11_used = any("group 11" in s.lower() or "qoi" in s.lower() for s in [prior_fungicide, seed_treatment])

    current_moa = " + ".join(set(f["group"] for f in fungicide_options))

    warnings = check_afren_compliance(
        crop="Canola",
        disease="blackleg",
        total_sprays=2 if prior_fungicide != "None" else 1,
        sdhis_used=sdhis_used,
        previous_moa=prior_fungicide,
        current_moa=current_moa,
        total_group_3_sprays=1 if group_3_used else 0,
        total_group_7_sprays=1 if sdhis_used else 0,
        total_group_11_sprays=1 if group_11_used else 0,
        blackleg_group_same_as_last_year=inputs.get("same_group_as_last_year", False),
        same_crop_last_2_years=inputs.get("same_crop_2_years", False),
        variety_resistance_rating=blackleg_rating,
        disease_visible=inputs.get("lesions_visible", False),
        fungicide_type="foliar",
        rain_forecast_hours=inputs.get("rain_forecast_hours", 0)
    )

    if spore_risk == "High" and inputs["crop_stage"] in ["2-leaf", "3-leaf", "4-leaf"]:
        if blackleg_rating in ["S", "MS", "MRMS"]:
            action = "Apply fungicide now"
        else:
            action = "Monitor closely or apply if yield potential is high"
    else:
        action = "Fungicide not required yet"

    if sdhis_used:
        fungicide_options = [f for f in fungicide_options if "SDHI" not in f["group"] and "Group 7" not in f["group"]]

    return {
        "variety": inputs["variety"],
        "blackleg_rating": blackleg_rating,
        "blackleg_group": blackleg_group,
        "spore_risk": spore_risk,
        "crop_stage": inputs["crop_stage"],
        "yield_potential": inputs["yield_potential"],
        "fungicide_cost": inputs["fungicide_cost"],
        "break_even_yield": break_even,
        "recommended_action": action,
        "fungicide_options": fungicide_options,
        "warnings": warnings
    }

# Example test
if __name__ == "__main__":
    test_inputs = {
        "variety": "Hunter",
        "crop_stage": "4-leaf",
        "yield_potential": 2.5,
        "grain_price": 650,
        "fungicide_cost": 35,
        "application_cost": 12,
        "rain_mm": 6.5,
        "rh_percent": 85,
        "temperature_c": 14,
        "previous_canola_stubble": True,
        "seed_treatment": "Saltro",
        "prior_fungicide": "Miravis Star",
        "same_group_as_last_year": True,
        "same_crop_2_years": False,
        "lesions_visible": False,
        "rain_forecast_hours": 24
    }

    result = evaluate_blackleg_risk(test_inputs)
    for key, value in result.items():
        print(f"{key.replace('_',' ').title()}: {value}")
