from fastapi import APIRouter,Query
from pathlib import Path
import pandas as pd
router=APIRouter(prefix="/data",tags=["Data"])
PATH=Path(__file__).resolve().parents[2]/"data"/"india_air_quality_total_320000.csv"
@router.get("/info")
def info():
    if not PATH.exists(): return {"available":False}
    cols=pd.read_csv(PATH,nrows=1).columns.tolist()
    return {"available":True,"records":320000,"columns":cols,"status":"synthetic development dataset"}
@router.get("/sample")
def sample(limit:int=Query(20,ge=1,le=1000)):
    if not PATH.exists(): return {"available":False}
    return pd.read_csv(PATH,nrows=limit).to_dict(orient="records")
