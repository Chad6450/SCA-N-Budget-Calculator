
# blackleg_risk_tool.py

# Extended variety resistance database
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

# Function to calculate spore release risk
def calculate_spore_risk(rain_mm, rh_percent, temperature_c):
    risk = 0
    if rain_mm >= 2:
        risk += 1
    if rh_percent >= 80:
        risk += 1
    if 10 <= temperature_c <= 20:
        risk += 1
    return "High" if risk >= 2 else "Moderate" if risk == 1 else "Low"

# Function to calculate break-even yield in kg/ha
def calculate_break_even_yield(fungicide_cost, application_cost, grain_price):
    total_cost = fungicide_cost + application_cost
    return round(total_cost / grain_price * 1000, 1)

# Main evaluation function
def evaluate_blackleg_risk(inputs):
    variety_info = variety_resistance_ratings.get(inputs["variety"], variety_resistance_ratings["Other"])
    spore_risk = calculate_spore_risk(inputs["rain_mm"], inputs["rh_percent"], inputs["temperature_c"])
    break_even = calculate_break_even_yield(inputs["fungicide_cost"], inputs["application_cost"], inputs["grain_price"])

    # Action recommendation logic
    if spore_risk == "High" and inputs["crop_stage"] in ["2-leaf", "3-leaf", "4-leaf"]:
        if variety_info.get("blackleg_rating") in ["S", "MS", "MRMS"]:
            action = "Apply fungicide now"
        else:
            action = "Monitor closely or apply if yield potential is high"
    else:
        action = "Fungicide not required yet"

    return {
        "variety": inputs["variety"],
        "blackleg_rating": variety_info.get("blackleg_rating", "Unknown"),
        "blackleg_group": variety_info.get("group", "Unknown"),
        "spore_risk": spore_risk,
        "crop_stage": inputs["crop_stage"],
        "yield_potential": inputs["yield_potential"],
        "fungicide_cost": inputs["fungicide_cost"],
        "break_even_yield": break_even,
        "recommended_action": action
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
        "previous_canola_stubble": True
    }

    result = evaluate_blackleg_risk(test_inputs)
    for key, value in result.items():
        print(f"{key.replace('_',' ').title()}: {value}")
