from fastapi import APIRouter
from pydantic import BaseModel,Field
router=APIRouter(prefix="/msme",tags=["MSME"])
class MSME(BaseModel):
    sector:str; fuel_consumption:float=Field(ge=0); electricity_kwh:float=Field(ge=0); annual_output:float=Field(gt=0)
@router.post("/assessment")
def assessment(x:MSME):
    total=x.fuel_consumption*2.75+x.electricity_kwh*.70
    return {"sector":x.sector,"estimated_co2e":total,"intensity":total/x.annual_output,"priority":"High" if total>100000 else "Standard"}
@router.post("/green-finance-screening")
def finance(x:MSME):
    total=x.fuel_consumption*2.75+x.electricity_kwh*.70
    return {"estimated_co2e":total,"screening_score":max(0,100-total/10000),"recommended_actions":["energy efficiency","clean fuel","dust control","emission monitoring"]}
