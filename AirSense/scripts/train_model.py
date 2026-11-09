"""Train an hourly PM2.5 next-step model from Open-Meteo's recent historical
air-quality series. This is a demonstration forecasting model, not an official
CPCB AQI forecast. It needs internet access during training.
"""
import os, sys, requests, joblib
import pandas as pd
from pathlib import Path
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from app.data_service import CITIES, OPEN_METEO_URL
from app.model import FEATURES

city = sys.argv[1] if len(sys.argv) > 1 else "Bengaluru"
if city not in CITIES:
    raise SystemExit(f"Choose one of: {', '.join(CITIES)}")
lat, lon = CITIES[city]
params = {
    "latitude": lat, "longitude": lon,
    "hourly": "pm2_5,pm10,nitrogen_dioxide,ozone",
    "past_days": 90, "forecast_days": 1, "timezone": "Asia/Kolkata"
}
print(f"Downloading recent air-quality series for {city}...")
response = requests.get(OPEN_METEO_URL, params=params, timeout=60)
response.raise_for_status()
hourly = response.json()["hourly"]
df = pd.DataFrame({
    "time": pd.to_datetime(hourly["time"]),
    "pm25": hourly.get("pm2_5"),
    "pm10": hourly.get("pm10"),
    "no2": hourly.get("nitrogen_dioxide"),
    "o3": hourly.get("ozone"),
})
df["hour"] = df["time"].dt.hour
df["dayofweek"] = df["time"].dt.dayofweek
df["target"] = df["pm25"].shift(-1)
df = df.dropna(subset=["pm25", "target"])
if len(df) < 300:
    raise SystemExit("Not enough usable data returned to train a model.")
X, y = df[FEATURES], df["target"]
split = int(len(df) * 0.8)
X_train, X_test, y_train, y_test = X.iloc[:split], X.iloc[split:], y.iloc[:split], y.iloc[split:]
pipeline = Pipeline([
    ("imputer", SimpleImputer(strategy="median")),
    ("model", RandomForestRegressor(n_estimators=250, max_depth=12, min_samples_leaf=2, random_state=42, n_jobs=-1))
])
pipeline.fit(X_train, y_train)
pred = pipeline.predict(X_test)
print(f"Chronological holdout MAE: {mean_absolute_error(y_test, pred):.2f} µg/m³")
print(f"Chronological holdout RMSE: {mean_squared_error(y_test, pred) ** 0.5:.2f} µg/m³")
print(f"Chronological holdout R²: {r2_score(y_test, pred):.3f}")
Path("models").mkdir(exist_ok=True)
joblib.dump(pipeline, "models/airsense_pm25_model.joblib")
print("Saved models/airsense_pm25_model.joblib")
print("Note: this model predicts next-hour PM2.5 from recent CAMS model series; it is not a certified monitoring-station forecast.")
