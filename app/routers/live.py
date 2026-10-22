from fastapi import APIRouter, HTTPException, Query

from app.services import cpcb_client as cpcb

router = APIRouter(prefix="/live", tags=["Live CPCB Data"])


def _load(state, city):
    try:
        return cpcb.client.fetch(state=state, city=city)
    except cpcb.CPCBUnavailable as exc:
        raise HTTPException(status_code=503, detail={
            "error": "CPCB live feed unavailable", "reason": str(exc),
            "source": cpcb.SOURCE,
        })


def _meta(data):
    meta = {k: data[k] for k in ("fetched_at", "feed_total", "rows_returned",
                                 "using_sample_key", "cached", "source")}
    meta["mode"] = data.get("mode", "live")
    if meta["mode"] == "snapshot":
        meta["snapshot_as_of"] = data.get("snapshot_as_of")
        meta["note"] = ("Saved CPCB snapshot: the live data.gov.in feed can't be reached from this server "
                        "(data.gov.in refuses connections from outside India). Readings are as of snapshot_as_of.")
        return meta
    if data["using_sample_key"]:
        meta["note"] = ("Public sample key: max 10 rows per request. Set "
                        "DATA_GOV_IN_API_KEY for the full station network.")
    return meta


@router.get("/status", summary="Check the CPCB live feed connection")
def status():
    data = _load(None, None)
    return {"status": "connected" if data.get("mode", "live") == "live" else "snapshot", **_meta(data)}


@router.get("/readings", summary="Raw pollutant readings from CPCB stations")
def readings(state: str | None = Query(None, examples=["Delhi"]),
             city: str | None = Query(None, examples=["Delhi"]),
             pollutant: str | None = Query(None, examples=["PM2.5"]),
             limit: int = Query(500, ge=1, le=5000)):
    data = _load(state, city)
    rows = data["rows"]
    if pollutant:
        p = cpcb.POLLUTANT_MAP.get(pollutant.strip().upper())
        if p is None:
            raise HTTPException(400, f"Unknown pollutant '{pollutant}'")
        rows = [r for r in rows if r["pollutant"] == p]
    return {**_meta(data), "count": len(rows[:limit]), "readings": rows[:limit]}


@router.get("/stations", summary="Station-level CPCB AQI (real data)")
def stations(state: str | None = Query(None, examples=["Haryana"]),
             city: str | None = Query(None, examples=["Faridabad"]),
             limit: int = Query(100, ge=1, le=1000)):
    data = _load(state, city)
    st = cpcb.station_aqi(data["rows"])
    return {**_meta(data), "count": len(st[:limit]), "stations": st[:limit]}


@router.get("/cities", summary="City AQI ranking from live CPCB stations")
def cities(state: str | None = Query(None), limit: int = Query(50, ge=1, le=500)):
    data = _load(state, None)
    summary = cpcb.city_summary(cpcb.station_aqi(data["rows"]))
    return {**_meta(data), "count": len(summary[:limit]), "cities": summary[:limit]}
