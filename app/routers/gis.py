from fastapi import APIRouter
router=APIRouter(prefix="/gis",tags=["GIS"])
@router.get("/hotspots")
def hotspots(): return {"method":"spatial hotspot framework","methods":["Getis-Ord Gi*","DBSCAN","KDE"],"output":"GeoJSON-ready"}
@router.get("/stations")
def stations(): return {"output":"GeoJSON-ready station layer"}
@router.get("/exposure")
def exposure(): return {"layers":["population","pollution","schools","hospitals","roads","industrial areas"],"output":"spatial exposure index"}
