import requests
from datetime import datetime, timezone

OPEN_METEO_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"
CITIES = {
    "Bengaluru": (12.9716, 77.5946),
    "Delhi": (28.6139, 77.2090),
    "Mumbai": (19.0760, 72.8777),
    "Chennai": (13.0827, 80.2707),
    "Hyderabad": (17.3850, 78.4867),
    "Kolkata": (22.5726, 88.3639),
    "Pune": (18.5204, 73.8567),
}

def get_air_quality(city: str):
    if city not in CITIES:
        raise ValueError("Unsupported city")
    lat, lon = CITIES[city]
    params = {
        "latitude": lat, "longitude": lon,
        "current": "pm10,pm2_5,carbon_monoxide,nitrogen_dioxide,sulphur_dioxide,ozone",
        "hourly": "pm10,pm2_5,nitrogen_dioxide,ozone",
        "forecast_days": 2, "timezone": "Asia/Kolkata"
    }
    response = requests.get(OPEN_METEO_URL, params=params, timeout=25)
    response.raise_for_status()
    return response.json()

def latest_hourly(data):
    hourly = data.get("hourly", {})
    times = hourly.get("time", [])
    if not times:
        return []
    result = []
    for i, stamp in enumerate(times):
        result.append({
            "time": stamp,
            "pm25": _at(hourly, "pm2_5", i),
            "pm10": _at(hourly, "pm10", i),
            "no2": _at(hourly, "nitrogen_dioxide", i),
            "o3": _at(hourly, "ozone", i),
        })
    return result

def _at(obj, key, index):
    values = obj.get(key) or []
    return values[index] if index < len(values) else None
