from fastapi import APIRouter
from pydantic import BaseModel,Field
router=APIRouter(prefix="/impact",tags=["Health & Economics"])
class Impact(BaseModel):
    population:int=Field(gt=0); exposure_index:float=Field(ge=0)
@router.post("/health")
def health(x:Impact):
    return {"population":x.population,"exposure_index":x.exposure_index,"risk_index":min(100,x.exposure_index*10),"note":"Screening index, not a clinical risk estimate."}
@router.post("/economic")
def economic(x:Impact):
    productivity_loss=x.population*x.exposure_index*100
    return {"estimated_screening_loss":productivity_loss,"currency":"INR","note":"Illustrative screening model; replace with validated local economic parameters."}
