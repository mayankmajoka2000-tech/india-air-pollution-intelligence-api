from fastapi import APIRouter
router=APIRouter(prefix="/analytics",tags=["Analytics"])
@router.get("/dashboard")
def dashboard():
    return {"metrics":["AQI","PM2.5","PM10","NO2","SO2","O3","CO","emissions","trend","hotspots","source contribution","forecast","policy impact"]}
@router.get("/rankings")
def rankings(): return {"ranking_types":["city","district","state_ut","station","source_sector"],"sort_options":["AQI","PM2.5","PM10","emissions","trend"]}
@router.get("/trends")
def trends(): return {"available":"dataset-dependent","analysis":["daily","weekly","monthly","seasonal","year-over-year"]}
