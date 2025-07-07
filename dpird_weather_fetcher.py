
import xarray as xr
import pandas as pd
import os
from datetime import datetime, timedelta

# Load station metadata with lat/lon using an absolute path
station_file = os.path.join(os.path.dirname(__file__), "dpird_stations.csv")
station_df = pd.read_csv(station_file)

# URLs to DPIRD OpenDAP datasets
RAIN_URL = "https://weather.dpird.wa.gov.au/thredds/dodsC/IDW60900.2024_Rainfall.nc"
TEMP_URL = "https://weather.dpird.wa.gov.au/thredds/dodsC/IDW60901.2024_Temp.nc"
RH_URL = "https://weather.dpird.wa.gov.au/thredds/dodsC/IDW60902.2024_RH.nc"

def find_station_location(code):
    row = station_df[station_df['code'] == code]
    if row.empty:
        raise ValueError(f"Station code {code} not found.")
    return float(row.iloc[0]['lat']), float(row.iloc[0]['lon'])

def fetch_variable_at_station(url, lat, lon, variable):
    ds = xr.open_dataset(url)
    lat_idx = abs(ds['lat'] - lat).argmin()
    lon_idx = abs(ds['lon'] - lon).argmin()
    last_valid = ds[variable].isel(lat=lat_idx, lon=lon_idx).dropna("time")[-1].values.item()
    return round(float(last_valid), 1)

def fetch_weather_from_dpird_live(code):
    try:
        lat, lon = find_station_location(code)

        rain_mm = fetch_variable_at_station(RAIN_URL, lat, lon, "rain_day")
        temperature_c = fetch_variable_at_station(TEMP_URL, lat, lon, "temp_mean")
        rh_percent = fetch_variable_at_station(RH_URL, lat, lon, "rh_mean")

        return {
            "rain_mm": rain_mm,
            "temperature_c": temperature_c,
            "rh_percent": rh_percent
        }
    except Exception as e:
        return {
            "rain_mm": 0.0,
            "temperature_c": 0.0,
            "rh_percent": 0.0,
            "error": str(e)
        }
