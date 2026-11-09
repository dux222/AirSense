from fastapi import FastAPI, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pathlib import Path
from app.db import init_db, SessionLocal, PredictionRecord
from app.data_service import CITIES, get_air_quality, latest_hourly
from app.aqi import estimate_india_aqi, category
from app.model import load_model, predict_next_pm25

app = FastAPI(title="AirSense API", description="Air quality monitoring and PM2.5 forecasting demo")
app.mount("/static", StaticFiles(directory="static"), name="static")
model = None

@app.on_event("startup")
def startup():
    global model
    init_db()
    model = load_model()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def home():
    return FileResponse("static/index.html")

@app.get("/api/cities")
def cities():
    return {"cities": list(CITIES.keys())}

@app.get("/api/air-quality")
def air_quality(city: str = "Bengaluru", db: Session = Depends(get_db)):
    try:
        data = get_air_quality(city)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Air-quality data provider unavailable: {exc}")
    current = data.get("current", {})
    pm25 = current.get("pm2_5")
    pm10 = current.get("pm10")
    aqi = estimate_india_aqi(pm25, pm10)
    label, advice = category(aqi)
    rows = latest_hourly(data)
    predicted = predict_next_pm25(model, rows)
    predicted_aqi = estimate_india_aqi(predicted, pm10) if predicted is not None else None
    if predicted is not None:
        db.add(PredictionRecord(city=city, predicted_pm25=predicted))
        db.commit()
    return {
        "city": city, "latitude": data.get("latitude"), "longitude": data.get("longitude"),
        "current": {
            "pm25": pm25, "pm10": pm10,
            "no2": current.get("nitrogen_dioxide"),
            "so2": current.get("sulphur_dioxide"),
            "o3": current.get("ozone"),
            "aqi_estimate": aqi, "category": label, "advice": advice
        },
        "prediction": {
            "next_hour_pm25": round(predicted, 2) if predicted is not None else None,
            "estimated_aqi": predicted_aqi,
            "model_available": model is not None
        },
        "hourly": rows[-24:],
        "source": "Open-Meteo Air Quality API (CAMS model data)"
    }

@app.get("/api/history")
def history(city: str = "Bengaluru", db: Session = Depends(get_db)):
    records = db.query(PredictionRecord).filter(PredictionRecord.city == city).order_by(PredictionRecord.created_at.desc()).limit(30).all()
    return {"records": [{"time": r.created_at.isoformat(), "predicted_pm25": r.predicted_pm25} for r in reversed(records)]}

@app.get("/api/health")
def health():
    return {"status": "ok", "model_loaded": model is not None}
