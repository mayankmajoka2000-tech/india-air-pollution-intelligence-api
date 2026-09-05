from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

router = APIRouter(
    prefix="/monitoring",
    tags=["Monitoring"]
)


class Observation(BaseModel):
    timestamp_utc: str
    city_ulb: str
    station_id: str

    pm25: Optional[float] = None
    pm10: Optional[float] = None
    no2: Optional[float] = None
    so2: Optional[float] = None
    co: Optional[float] = None
    o3: Optional[float] = None
    nh3: Optional[float] = None
    pb: Optional[float] = None


@router.post("/ingest")
def ingest(records: list[Observation]):
    return {
        "accepted": len(records),
        "status": "validated_for_ingestion"
    }


@router.post("/batch")
def batch(records: list[Observation]):
    return {
        "accepted": len(records),
        "batch_status": "ready_for_database"
    }


@router.post("/anomaly")
def anomaly(values: list[float]):
    if not values:
        return {
            "anomaly_count": 0,
            "indices": [],
            "method": "IQR"
        }

    import numpy as np

    a = np.array(values, dtype=float)

    q1 = np.percentile(a, 25)
    q3 = np.percentile(a, 75)

    iqr = q3 - q1

    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr

    idx = np.where(
        (a < lower_bound) | (a > upper_bound)
    )[0].tolist()

    return {
        "anomaly_count": len(idx),
        "indices": idx,
        "method": "IQR",
        "lower_bound": round(float(lower_bound), 2),
        "upper_bound": round(float(upper_bound), 2)
    }
