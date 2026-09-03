from fastapi import APIRouter
from pydantic import BaseModel
router=APIRouter(prefix="/alerts",tags=["Alerts"])
class Alert(BaseModel):
    pollutant:str; value:float; threshold:float
@router.post("/evaluate")
def evaluate(x:Alert):
    triggered=x.value>=x.threshold
    return {"triggered":triggered,"pollutant":x.pollutant,"value":x.value,"threshold":x.threshold,"severity":"HIGH" if triggered else "NORMAL"}
