from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.services.cpcb_aqi import (AVERAGING, BREAKPOINTS, INDEX_BANDS, UNITS,
                                   calculate_cpcb_aqi, category, sub_index)

router = APIRouter(prefix="/aqi", tags=["AQI"])


class Pollutants(BaseModel):
    """Concentrations: CO in mg/m3, all others in ug/m3. Omit pollutants not measured."""
    pm25: float | None = Field(None, ge=0, description="PM2.5, 24-h avg, ug/m3")
    pm10: float | None = Field(None, ge=0, description="PM10, 24-h avg, ug/m3")
    no2: float | None = Field(None, ge=0, description="NO2, 24-h avg, ug/m3")
    so2: float | None = Field(None, ge=0, description="SO2, 24-h avg, ug/m3")
    co: float | None = Field(None, ge=0, description="CO, 8-h avg, mg/m3")
    o3: float | None = Field(None, ge=0, description="O3, 8-h avg, ug/m3")
    nh3: float | None = Field(None, ge=0, description="NH3, 24-h avg, ug/m3")
    pb: float | None = Field(None, ge=0, description="Pb, 24-h avg, ug/m3")


def cat(a):
    """Kept for backward compatibility."""
    return category(a)


@router.post("/calculate", summary="CPCB National AQI from concentrations")
def calculate(p: Pollutants):
    result = calculate_cpcb_aqi(p.model_dump())
    result["method"] = "CPCB National Air Quality Index breakpoints (CUPS/82/2014-15)"
    return result


@router.get("/sub-index", summary="Sub-index for a single pollutant")
def single(pollutant: str = Query(..., examples=["PM2.5"]),
           concentration: float = Query(..., ge=0)):
    try:
        si = sub_index(pollutant, concentration)
    except ValueError as exc:
        raise HTTPException(400, str(exc))
    return {"pollutant": pollutant, "concentration": concentration,
            "sub_index": si, "category": category(si)}


@router.get("/breakpoints", summary="Official CPCB breakpoint table")
def breakpoints():
    return {
        p: {"unit": UNITS[p], "averaging": AVERAGING[p],
            "bands": [{"index": f"{lo}-{hi}", "concentration": [b_lo, b_hi]}
                      for (lo, hi), (b_lo, b_hi) in zip(INDEX_BANDS, bands)]}
        for p, bands in BREAKPOINTS.items()
    }
