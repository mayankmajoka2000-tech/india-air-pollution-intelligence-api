from fastapi import APIRouter
from pydantic import BaseModel
router=APIRouter(prefix="/source-attribution",tags=["Source Attribution"])
class Contributions(BaseModel):
    transport:float=0; industry:float=0; power:float=0; construction:float=0; road_dust:float=0; waste:float=0; agriculture:float=0; residential:float=0
@router.post("/normalize")
def normalize(x:Contributions):
    d=x.model_dump(); total=sum(d.values())
    return {"total":total,"shares":{k:(v/total*100 if total else 0) for k,v in d.items()},"method":"input contribution normalization"}
@router.post("/scenario")
def scenario(x:Contributions):
    d=x.model_dump(); total=sum(d.values())
    return {"baseline":d,"total":total,"top_source":max(d,key=d.get) if total else None}
