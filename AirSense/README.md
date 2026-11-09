# AirSense — AI-Powered Air Quality Prediction

AirSense is an academic full-stack prototype for exploring air quality and experimenting with a one-hour-ahead PM2.5 machine-learning forecast.

## Features
- City selector for Bengaluru, Delhi, Mumbai, Chennai, Hyderabad, Kolkata and Pune.
- Current pollutant readings and hourly PM2.5 / PM10 charts.
- CPCB-style AQI estimate from PM2.5 and PM10 only.
- Optional Random Forest model for next-hour PM2.5 prediction.
- Prediction history stored using SQLite by default; MySQL is supported by configuration.
- FastAPI REST API and responsive HTML/CSS/JavaScript dashboard.

## Important data and model limitations
- Live/hourly environmental data comes from the Open-Meteo Air Quality API, based on CAMS atmospheric composition model data. It is modelled gridded data, not a physical sensor reading at the exact address or an official CPCB station observation.
- The displayed India-style AQI is an estimate using only PM2.5 and PM10 sub-indices. Official CPCB AQI requires the prescribed pollutant coverage, averaging windows and validity checks. Do not describe this estimate as an official CPCB AQI.
- The ML training script uses the recent hourly Open-Meteo series and predicts the next-hour PM2.5 value. It is an educational model, not a certified forecast. Its holdout metrics are printed at training time.
- Without a trained model file, live readings and charts still work; the ML prediction panel correctly reports that the model has not yet been trained.

## Setup (Windows PowerShell)
```powershell
py -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Train the model (requires internet):
```powershell
python -m scripts.train_model Bengaluru
```
You can also train for another supported city:
```powershell
python -m scripts.train_model Delhi
```

Start the application:
```powershell
uvicorn app.main:app --reload
```
Open http://127.0.0.1:8000

API documentation: http://127.0.0.1:8000/docs

## Database
SQLite is used by default and creates `airsense.db` automatically.
To use MySQL, create a database named `airsense`, copy `.env.example` to `.env`, and set:
```env
DATABASE_URL=mysql+pymysql://username:password@localhost:3306/airsense
```
Restart the app. The SQLAlchemy model will create the prediction_history table.

## Project structure
```text
AirSense/
├── app/                 # FastAPI, data provider, AQI and model logic
├── static/              # Frontend dashboard
├── scripts/             # Model training script
├── models/              # Trained model saved here (created by training)
├── data/                # Optional datasets
├── requirements.txt
└── README.md
```

## Data source and attribution
Air quality data: [Open-Meteo Air Quality API](https://open-meteo.com/en/docs/air-quality-api). The API documentation identifies CAMS forecast/reanalysis sources. Please retain attribution to Open-Meteo and CAMS when redistributing data-derived outputs. CPCB AQI framework reference: [CPCB National AQI](https://www.airquality.cpcb.gov.in/AQI/).

## Suggested next improvements
- Replace the CAMS-based training series with quality-controlled CPCB station observations for station-specific modelling.
- Add weather predictors and lagged time-series features.
- Use walk-forward validation and compare persistence, linear regression, random forest and gradient boosting baselines.
- Add user authentication, alert preferences, station-level maps and deployment monitoring.
