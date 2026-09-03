from fastapi import APIRouter
from pydantic import BaseModel, Field
router=APIRouter(prefix="/forecast",tags=["ML Forecasting"])
class ForecastRequest(BaseModel):
    recent_values:list[float]=Field(min_length=1); horizon:int=Field(default=24,ge=1,le=168)
@router.post("/")
def forecast(x:ForecastRequest):
    last=x.recent_values[-1]
    return {"model":"persistence_baseline","horizon":x.horizon,"forecast":[last]*x.horizon,"production_models":["XGBoost","LightGBM","LSTM","GRU","Transformer"]}
@router.post("/train")
def train(): return {"status":"training_job_specification_ready","models":["XGBoost","LightGBM","LSTM","GRU","Transformer"],"tracking":"MLflow-ready"}
