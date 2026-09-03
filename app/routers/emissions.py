from fastapi import APIRouter
from pydantic import BaseModel, Field
router=APIRouter(prefix="/emissions",tags=["Emissions"])
class Emission(BaseModel):
    activity: float=Field(gt=0)
    emission_factor: float=Field(gt=0)
    control_efficiency: float=Field(default=0,ge=0,le=1)
@router.post("/calculate")
def calculate(x:Emission):
    gross=x.activity*x.emission_factor; net=gross*(1-x.control_efficiency)
    return {"gross":gross,"net":net,"avoided":gross-net}
@router.post("/scenario")
def scenario(x:Emission):
    gross=x.activity*x.emission_factor
    return {"baseline":gross,"scenarios":[{"control_pct":p,"net":gross*(1-p/100),"reduction":gross*p/100} for p in [0,10,25,50,75,90]]}
