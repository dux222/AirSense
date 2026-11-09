from pathlib import Path
import joblib
import pandas as pd
import numpy as np

MODEL_FILE = Path("models/airsense_pm25_model.joblib")
FEATURES = ["pm25", "pm10", "no2", "o3", "hour", "dayofweek"]

def load_model():
    if MODEL_FILE.exists():
        return joblib.load(MODEL_FILE)
    return None

def predict_next_pm25(model, rows):
    if model is None or not rows:
        return None
    valid = [r for r in rows if r.get("pm25") is not None]
    if len(valid) < 2:
        return None
    last = valid[-1]
    stamp = pd.to_datetime(last["time"])
    row = {
        "pm25": float(last["pm25"]),
        "pm10": float(last["pm10"] or 0),
        "no2": float(last["no2"] or 0),
        "o3": float(last["o3"] or 0),
        "hour": stamp.hour,
        "dayofweek": stamp.dayofweek,
    }
    return float(model.predict(pd.DataFrame([row], columns=FEATURES))[0])
