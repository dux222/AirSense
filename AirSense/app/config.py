import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL") or "sqlite:///./airsense.db"
MODEL_PATH = "models/airsense_pm25_model.joblib"
