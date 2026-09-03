from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
router=APIRouter(prefix="/monitoring",tags=["Monitoring"])
class Observation(BaseModel):
    timestamp_utc:str; city_ulb:str; station_id:str
    pm25:Optional[float]=None; pm10:Optional[float]=None; no2:Optional[float]=None; so2:Optional[float]=None
    co:Optional[float]=None; o3:Optional[float]=None; nh3:Optional[float]=None; pb:Optional[float]=None
@router.post("/ingest")
def ingest(records:list[Observation]): return {"accepted":len(records),"status":"validated_for_ingestion"}
@router.post("/batch")
def batch(records:list[Observation]): return {"accepted":len(records),"batch_status":"ready_for_database"}
@router.post("/anomaly")
def anomaly(values:list[float]):
    if not values:return {"anomalies":[]}
    import numpy as np
    a=np.array(values,float); z=np.abs((a-a.mean())/(a.std() or 1))
    idx=np.where(z>3)[0].tolist()
    return {"anomaly_count":len(idx),"indices":idx,"method":"z-score"}
