"""
Live CPCB data client.

Source: CPCB "Real time Air Quality Index from various locations", published on
the Open Government Data Platform India (data.gov.in), resource
3b01bcb8-0b14-4abf-b6f2-c1bfd384ba69. Licence: Government Open Data Licence -
India (GODL). The feed is refreshed hourly from CPCB's CAAQMS station network.

Each feed row is one pollutant at one station: state, city, station,
last_update, pollutant_id, and min / max / avg values over the last 24 hours.
Field names changed over time (pollutant_avg vs avg_value), so both are read.

Configuration (environment variables):
  DATA_GOV_IN_API_KEY   your personal key from data.gov.in (free sign-up).
                        Without it the public sample key is used, which
                        returns at most 10 rows per request.
  CPCB_FEED_VALUES      "sub_index" (default): the feed's per-pollutant values
                        are CPCB index values, so station AQI = max of them.
                        "concentration": values are treated as concentrations
                        and converted with the CPCB breakpoint tables.
  CPCB_CACHE_SECONDS    in-memory cache lifetime, default 900 (15 minutes).
"""
from __future__ import annotations

import os
import time
from datetime import datetime, timezone
from typing import Any

import httpx

from app.services.cpcb_aqi import aggregate_sub_indices, calculate_cpcb_aqi

RESOURCE_ID = "3b01bcb8-0b14-4abf-b6f2-c1bfd384ba69"
BASE_URL = f"https://api.data.gov.in/resource/{RESOURCE_ID}"
SAMPLE_KEY = "579b464db66ec23bdd000001cdd3946e44ce4aad7209ff7b23ac571b"
SOURCE = {
    "publisher": "Central Pollution Control Board (CPCB), Government of India",
    "platform": "Open Government Data Platform India (data.gov.in)",
    "resource_id": RESOURCE_ID,
    "dataset": "Real time Air Quality Index from various locations",
    "licence": "Government Open Data Licence - India (GODL)",
    "url": "https://data.gov.in/resource/real-time-air-quality-index-various-locations",
}

POLLUTANT_MAP = {
    "PM2.5": "PM2.5", "PM10": "PM10", "NO2": "NO2", "SO2": "SO2",
    "CO": "CO", "OZONE": "O3", "O3": "O3", "NH3": "NH3", "PB": "Pb",
}


class CPCBUnavailable(RuntimeError):
    """Raised when the live feed cannot be reached or returns an error."""


def _api_key() -> tuple[str, bool]:
    key = os.getenv("DATA_GOV_IN_API_KEY", "").strip()
    return (key, False) if key else (SAMPLE_KEY, True)


def _num(value: Any) -> float | None:
    if value is None:
        return None
    s = str(value).strip()
    if s in ("", "NA", "NaN", "None", "-"):
        return None
    try:
        return float(s)
    except ValueError:
        return None


def _parse_time(value: str | None) -> str | None:
    if not value:
        return None
    for fmt in ("%d-%m-%Y %H:%M:%S", "%Y-%m-%d %H:%M:%S", "%d-%m-%Y %H:%M"):
        try:
            # CPCB timestamps are Indian Standard Time.
            return datetime.strptime(value.strip(), fmt).strftime("%Y-%m-%dT%H:%M:%S+05:30")
        except ValueError:
            continue
    return value


def normalise_record(raw: dict) -> dict | None:
    """Turn one feed row into a clean dict. Returns None for unusable rows."""
    pollutant = POLLUTANT_MAP.get(str(raw.get("pollutant_id", "")).strip().upper())
    if pollutant is None:
        return None
    return {
        "state": str(raw.get("state", "")).replace("_", " ").strip(),
        "city": str(raw.get("city", "")).strip(),
        "station": str(raw.get("station", "")).strip(),
        "latitude": _num(raw.get("latitude")),
        "longitude": _num(raw.get("longitude")),
        "last_update": _parse_time(raw.get("last_update")),
        "pollutant": pollutant,
        "min": _num(raw.get("min_value", raw.get("pollutant_min"))),
        "max": _num(raw.get("max_value", raw.get("pollutant_max"))),
        "avg": _num(raw.get("avg_value", raw.get("pollutant_avg"))),
    }


class CPCBClient:
    def __init__(self, timeout: float = 20.0, transport: httpx.BaseTransport | None = None):
        self.timeout = timeout
        self.transport = transport
        self.cache_seconds = int(os.getenv("CPCB_CACHE_SECONDS", "900"))
        self._cache: dict[tuple, tuple[float, dict]] = {}

    # ---------------------------------------------------------------- fetch
    def _get(self, params: dict) -> dict:
        try:
            with httpx.Client(timeout=self.timeout, transport=self.transport) as c:
                r = c.get(BASE_URL, params=params)
        except httpx.HTTPError as exc:
            raise CPCBUnavailable(f"Could not reach data.gov.in: {exc}") from exc
        if r.status_code != 200:
            raise CPCBUnavailable(f"data.gov.in returned HTTP {r.status_code}")
        try:
            payload = r.json()
        except ValueError as exc:
            raise CPCBUnavailable("data.gov.in returned a non-JSON response") from exc
        if str(payload.get("status", "ok")).lower() == "error":
            raise CPCBUnavailable(payload.get("message", "data.gov.in error"))
        return payload

    def fetch(self, state: str | None = None, city: str | None = None,
              max_rows: int = 5000) -> dict:
        """Fetch normalised rows, paging through the feed. Cached per filter."""
        cache_key = (state, city, max_rows)
        hit = self._cache.get(cache_key)
        if hit and time.time() - hit[0] < self.cache_seconds:
            return {**hit[1], "cached": True}

        key, sample = _api_key()
        page = 10 if sample else 1000
        params: dict[str, Any] = {"api-key": key, "format": "json", "limit": page}
        if state:
            params["filters[state]"] = state.replace(" ", "_")
        if city:
            params["filters[city]"] = city

        rows: list[dict] = []
        total = None
        offset = 0
        while offset < max_rows:
            params["offset"] = offset
            payload = self._get(params)
            records = payload.get("records", []) or []
            total = int(payload.get("total", len(records)) or 0)
            rows.extend(r for r in (normalise_record(x) for x in records) if r)
            offset += page
            if sample or not records or offset >= total:
                break

        result = {
            "rows": rows,
            "feed_total": total,
            "rows_returned": len(rows),
            "using_sample_key": sample,
            "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "source": SOURCE,
            "cached": False,
        }
        self._cache[cache_key] = (time.time(), result)
        return result


# ---------------------------------------------------------------- analytics
def station_aqi(rows: list[dict]) -> list[dict]:
    """Group pollutant rows by station and compute the CPCB AQI per station."""
    mode = os.getenv("CPCB_FEED_VALUES", "sub_index").strip().lower()
    stations: dict[tuple, dict] = {}
    for r in rows:
        k = (r["state"], r["city"], r["station"])
        s = stations.setdefault(k, {
            "state": r["state"], "city": r["city"], "station": r["station"],
            "latitude": r["latitude"], "longitude": r["longitude"],
            "last_update": r["last_update"], "pollutants": {},
        })
        if r["avg"] is not None:
            s["pollutants"][r["pollutant"]] = {"avg": r["avg"], "min": r["min"], "max": r["max"]}
        if r["last_update"] and (s["last_update"] is None or r["last_update"] > s["last_update"]):
            s["last_update"] = r["last_update"]

    out = []
    for s in stations.values():
        avgs = {p: v["avg"] for p, v in s["pollutants"].items()}
        if mode == "concentration":
            aqi = calculate_cpcb_aqi(avgs)
        else:
            aqi = aggregate_sub_indices(avgs)
        out.append({**s, **{k: aqi[k] for k in ("aqi", "category", "prominent_pollutant", "valid")},
                    "value_interpretation": mode})
    out.sort(key=lambda x: (x["aqi"] is None, -(x["aqi"] or 0)))
    return out


def city_summary(stations: list[dict]) -> list[dict]:
    """City-level roll-up: mean / max of valid station AQIs."""
    from app.services.cpcb_aqi import category

    cities: dict[tuple, list[dict]] = {}
    for s in stations:
        cities.setdefault((s["state"], s["city"]), []).append(s)
    out = []
    for (state, city), ss in cities.items():
        vals = [s["aqi"] for s in ss if s["aqi"] is not None]
        mean = round(sum(vals) / len(vals)) if vals else None
        worst = max(ss, key=lambda s: s["aqi"] or -1)
        out.append({
            "state": state, "city": city,
            "stations": len(ss), "stations_with_valid_aqi": len(vals),
            "mean_aqi": mean, "category": category(mean) if mean is not None else None,
            "max_aqi": worst["aqi"], "worst_station": worst["station"] if vals else None,
        })
    out.sort(key=lambda x: (x["mean_aqi"] is None, -(x["mean_aqi"] or 0)))
    return out


client = CPCBClient()
