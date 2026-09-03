from fastapi import APIRouter
from pydantic import BaseModel
router=APIRouter(prefix="/aqi",tags=["AQI"])
class Pollutants(BaseModel):
    pm25:float=0; pm10:float=0; no2:float=0; so2:float=0; co:float=0; o3:float=0; nh3:float=0; pb:float=0
def cat(a):
    return "Good" if a<=50 else "Satisfactory" if a<=100 else "Moderate" if a<=200 else "Poor" if a<=300 else "Very Poor" if a<=400 else "Severe"
@router.post("/calculate")
def calculate(p:Pollutants):
    scores={"PM2.5":min(p.pm25*2,500),"PM10":min(p.pm10,500),"NO2":min(p.no2*1.5,500),"SO2":min(p.so2*2,500),"CO":min(p.co*50,500),"O3":min(p.o3*1.5,500),"NH3":min(p.nh3*2,500),"Pb":min(p.pb*100,500)}
    a=max(scores.values())
    return {"aqi":round(a),"category":cat(a),"pollutant_scores":scores,"note":"Use official CPCB breakpoint tables for regulated production scoring."}
