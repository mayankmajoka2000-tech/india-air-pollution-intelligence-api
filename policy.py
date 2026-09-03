from fastapi import APIRouter
from pydantic import BaseModel, Field
router=APIRouter(prefix="/policy",tags=["Policy"])
class Policy(BaseModel):
    baseline_emission:float=Field(gt=0); measures:list[dict]
@router.post("/simulate")
def simulate(x:Policy):
    out=[]
    for m in x.measures:
        r=float(m.get("reduction_pct",0)); cost=float(m.get("cost",0)); net=x.baseline_emission*(1-r/100)
        out.append({"measure":m.get("name","unnamed"),"reduction_pct":r,"net_emission":net,"cost":cost,"cost_per_unit_reduction":cost/(x.baseline_emission-net) if net<x.baseline_emission else None})
    return {"baseline":x.baseline_emission,"scenarios":out}
@router.post("/optimize")
def optimize(x:Policy):
    scored=[]
    for m in x.measures:
        r=float(m.get("reduction_pct",0)); cost=float(m.get("cost",0))
        scored.append((cost/max(r,1e-9),m))
    scored.sort(key=lambda z:z[0])
    return {"ranking":[{"measure":m.get("name","unnamed"),"cost_efficiency":score} for score,m in scored],"objective":"maximize pollution reduction per unit cost"}
