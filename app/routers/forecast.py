from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from pathlib import Path
import joblib
import pandas as pd


router = APIRouter(
    prefix="/forecast",
    tags=["ML Forecasting"]
)


# ============================================================
# MODEL PATH
# ============================================================

MODEL_PATH = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "models"
    / "best_pm25_model.joblib"
)


# ============================================================
# MODEL FEATURES
# ============================================================

FEATURES = [
    "PM10_ug_m3",
    "NO2_ug_m3",
    "SO2_ug_m3",
    "CO_mg_m3",
    "O3_ug_m3",
    "NH3_ug_m3",
    "Pb_ug_m3",
    "temperature_C",
    "relative_humidity_pct",
    "wind_speed_m_s",
    "wind_direction_deg",
    "rainfall_mm",
    "pressure_hPa"
]


# ============================================================
# REQUEST MODELS
# ============================================================

class ForecastRequest(BaseModel):
    recent_values: list[float] = Field(min_length=1)

    horizon: int = Field(
        default=24,
        ge=1,
        le=168
    )


class PM25PredictionRequest(BaseModel):

    PM10_ug_m3: float = Field(ge=0)
    NO2_ug_m3: float = Field(ge=0)
    SO2_ug_m3: float = Field(ge=0)
    CO_mg_m3: float = Field(ge=0)
    O3_ug_m3: float = Field(ge=0)
    NH3_ug_m3: float = Field(ge=0)
    Pb_ug_m3: float = Field(ge=0)

    temperature_C: float

    relative_humidity_pct: float = Field(
        ge=0,
        le=100
    )

    wind_speed_m_s: float = Field(ge=0)

    wind_direction_deg: float = Field(
        ge=0,
        le=360
    )

    rainfall_mm: float = Field(ge=0)
    pressure_hPa: float = Field(ge=0)


# ============================================================
# LOAD TRAINED MODEL ONCE
# ============================================================

MODEL = None

if MODEL_PATH.exists():

    try:
        MODEL = joblib.load(MODEL_PATH)

    except Exception:
        MODEL = None


def load_model():

    if MODEL is None:

        raise HTTPException(
            status_code=503,
            detail=(
                "Trained Random Forest model is not available. "
                "Please deploy the trained model artifact first."
            )
        )

    return MODEL


# ============================================================
# EXISTING FORECAST ENDPOINT
# ============================================================

@router.post("/")
def forecast(x: ForecastRequest):

    last = x.recent_values[-1]

    return {
        "model": "persistence_baseline",
        "horizon": x.horizon,
        "forecast": [last] * x.horizon,
        "production_models": [
            "Random Forest",
            "XGBoost",
            "LightGBM",
            "LSTM",
            "GRU",
            "Transformer"
        ]
    }


# ============================================================
# TRAINED RANDOM FOREST PM2.5 PREDICTION
# ============================================================

@router.post("/predict")
def predict_pm25(x: PM25PredictionRequest):

    model = load_model()

    input_data = pd.DataFrame(
        [[
            x.PM10_ug_m3,
            x.NO2_ug_m3,
            x.SO2_ug_m3,
            x.CO_mg_m3,
            x.O3_ug_m3,
            x.NH3_ug_m3,
            x.Pb_ug_m3,
            x.temperature_C,
            x.relative_humidity_pct,
            x.wind_speed_m_s,
            x.wind_direction_deg,
            x.rainfall_mm,
            x.pressure_hPa
        ]],
        columns=FEATURES
    )

    prediction = float(
        model.predict(input_data)[0]
    )

    return {
        "model": "Random Forest",
        "target": "PM2.5",
        "predicted_PM25_ug_m3": round(
            prediction,
            4
        ),
        "unit": "µg/m³",
        "model_status": "trained",
        "dataset_records": 320000,
        "development_dataset": True
    }


# ============================================================
# MODEL INFORMATION
# ============================================================

@router.get("/model-info")
def model_info():

    return {
        "model": "Random Forest",
        "target": "PM2.5",
        "status": (
            "available"
            if MODEL_PATH.exists()
            else "not_available"
        ),
        "model_file": str(MODEL_PATH),
        "training_records": 320000,
        "features": FEATURES,
        "MAE": 5.8700,
        "RMSE": 8.2894,
        "R2": 0.9484,
        "dataset_status": "synthetic development dataset",
        "warning": (
            "Performance metrics are based on the synthetic "
            "development dataset and should not be interpreted "
            "as real-world CPCB validation."
        )
    }


# ============================================================
# TRAINING JOB INFORMATION
# ============================================================

@router.post("/train")
def train():

    return {
        "status": "training_job_specification_ready",
        "selected_model": "Random Forest",
        "models": [
            "Random Forest",
            "XGBoost",
            "LightGBM",
            "LSTM",
            "GRU",
            "Transformer"
        ],
        "tracking": "MLflow-ready",
        "note": (
            "Training is currently performed through "
            "the GitHub Actions ML pipeline."
        )
    }
