"""
CPCB National Air Quality Index (NAQI) engine.

Implements the official CPCB breakpoint tables (CPCB, "National Air Quality
Index", Control of Urban Pollution Series CUPS/82/2014-15) with piecewise
linear interpolation:

    I = (I_hi - I_lo) / (B_hi - B_lo) * (C - B_lo) + I_lo

Averaging periods per CPCB: 24-hour for PM10, PM2.5, NO2, SO2, NH3, Pb;
8-hour for CO and O3 (O3 may also use 1-hour). CO is in mg/m3, all others
in ug/m3.

The overall AQI is the maximum sub-index, reported only when at least three
pollutants are available and at least one of them is PM10 or PM2.5 (CPCB rule).

CPCB does not publish an upper concentration bound for the "Severe" band;
NOMINAL_SEVERE_UPPER below is a documented modelling assumption used to
interpolate 401-500, and the result is capped at 500.
"""
from __future__ import annotations

INDEX_BANDS = [(0, 50), (51, 100), (101, 200), (201, 300), (301, 400), (401, 500)]

CATEGORIES = ["Good", "Satisfactory", "Moderate", "Poor", "Very Poor", "Severe"]

HEALTH_IMPACT = {
    "Good": "Minimal impact",
    "Satisfactory": "Minor breathing discomfort to sensitive people",
    "Moderate": "Breathing discomfort to people with lung, heart disease, children and older adults",
    "Poor": "Breathing discomfort to most people on prolonged exposure",
    "Very Poor": "Respiratory illness on prolonged exposure",
    "Severe": "Affects healthy people and seriously impacts those with existing diseases",
}

# Concentration breakpoints (lower, upper) per index band, from the CPCB NAQI table.
BREAKPOINTS: dict[str, list[tuple[float, float]]] = {
    "PM10": [(0, 50), (51, 100), (101, 250), (251, 350), (351, 430), (431, None)],
    "PM2.5": [(0, 30), (31, 60), (61, 90), (91, 120), (121, 250), (251, None)],
    "NO2": [(0, 40), (41, 80), (81, 180), (181, 280), (281, 400), (401, None)],
    "O3": [(0, 50), (51, 100), (101, 168), (169, 208), (209, 748), (749, None)],
    "CO": [(0, 1.0), (1.1, 2.0), (2.1, 10), (10.1, 17), (17.1, 34), (34.1, None)],
    "SO2": [(0, 40), (41, 80), (81, 380), (381, 800), (801, 1600), (1601, None)],
    "NH3": [(0, 200), (201, 400), (401, 800), (801, 1200), (1201, 1800), (1801, None)],
    "Pb": [(0, 0.5), (0.6, 1.0), (1.1, 2.0), (2.1, 3.0), (3.1, 3.5), (3.6, None)],
}

UNITS = {p: ("mg/m3" if p == "CO" else "ug/m3") for p in BREAKPOINTS}
AVERAGING = {p: ("8-hour" if p in ("CO", "O3") else "24-hour") for p in BREAKPOINTS}

# Assumption (not CPCB): concentration at which the Severe band reaches 500.
NOMINAL_SEVERE_UPPER = {
    "PM10": 600, "PM2.5": 380, "NO2": 500, "O3": 1000,
    "CO": 50, "SO2": 2100, "NH3": 2400, "Pb": 4.0,
}

ALIASES = {
    "pm25": "PM2.5", "pm2.5": "PM2.5", "pm2_5": "PM2.5",
    "pm10": "PM10", "no2": "NO2", "so2": "SO2", "co": "CO",
    "o3": "O3", "ozone": "O3", "nh3": "NH3", "pb": "Pb", "lead": "Pb",
}


def normalise_pollutant(name: str) -> str | None:
    key = name.strip()
    if key in BREAKPOINTS:
        return key
    return ALIASES.get(key.lower())


def category(aqi: float) -> str:
    for (lo, hi), cat in zip(INDEX_BANDS, CATEGORIES):
        if aqi <= hi:
            return cat
    return "Severe"


def sub_index(pollutant: str, concentration: float) -> int:
    """Sub-index (0-500) for one pollutant concentration using CPCB breakpoints."""
    p = normalise_pollutant(pollutant)
    if p is None:
        raise ValueError(f"Unknown pollutant: {pollutant}")
    if concentration is None or concentration < 0:
        raise ValueError("Concentration must be a non-negative number")

    bands = BREAKPOINTS[p]
    for i, (b_lo, b_hi) in enumerate(bands):
        i_lo, i_hi = INDEX_BANDS[i]
        if b_hi is None:
            b_hi = NOMINAL_SEVERE_UPPER[p]
        # Treat the gap between one band's upper and the next band's lower
        # (e.g. PM2.5 30 -> 31) as belonging to the lower band's top edge.
        next_lo = bands[i + 1][0] if i + 1 < len(bands) else None
        if next_lo is None or concentration < next_lo:
            c = min(max(concentration, b_lo), b_hi)
            value = (i_hi - i_lo) / (b_hi - b_lo) * (c - b_lo) + i_lo
            return int(round(min(value, 500)))
    return 500


def calculate_cpcb_aqi(concentrations: dict[str, float | None]) -> dict:
    """
    Overall AQI from pollutant concentrations.

    Returns aqi=None when the CPCB minimum-data rule is not met.
    """
    subs: dict[str, int] = {}
    for name, value in concentrations.items():
        p = normalise_pollutant(name)
        if p is None or value is None:
            continue
        subs[p] = sub_index(p, float(value))

    return aggregate_sub_indices(subs)


def aggregate_sub_indices(subs: dict[str, float]) -> dict:
    """Apply the CPCB aggregation rule to already-computed sub-indices."""
    subs = {k: v for k, v in subs.items() if v is not None}
    has_pm = "PM10" in subs or "PM2.5" in subs
    valid = len(subs) >= 3 and has_pm

    if not subs:
        return {"aqi": None, "category": None, "prominent_pollutant": None,
                "sub_indices": {}, "valid": False,
                "reason": "No pollutant data"}

    prominent = max(subs, key=subs.get)
    aqi = int(round(subs[prominent])) if valid else None
    result = {
        "aqi": aqi,
        "category": category(aqi) if aqi is not None else None,
        "health_impact": HEALTH_IMPACT[category(aqi)] if aqi is not None else None,
        "prominent_pollutant": prominent if valid else None,
        "sub_indices": subs,
        "pollutants_used": len(subs),
        "valid": valid,
    }
    if not valid:
        result["reason"] = ("CPCB requires at least 3 pollutants including "
                            "PM10 or PM2.5")
    return result
