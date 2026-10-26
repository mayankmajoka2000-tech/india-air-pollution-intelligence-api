from fastapi import FastAPI, Request
from pathlib import Path
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from app.routers import health, india, emissions, aqi, monitoring, forecast, policy, msme, analytics, gis, auth, data, alerts, health_impact, source_attribution, live

app = FastAPI(
    title="India Air Pollution Intelligence API",
    swagger_ui_parameters={"deepLinking": True, "displayRequestDuration": True, "syntaxHighlight.theme": "obsidian"},
    version="5.0.0",
    description="India-scale air pollution intelligence platform covering monitoring, emissions, AQI, forecasting, GIS, source attribution, policy, MSMEs, health/economic impacts, alerts and ML."
)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

for r in [health.router, india.router, emissions.router, aqi.router, monitoring.router,
          forecast.router, policy.router, msme.router, analytics.router, gis.router,
          auth.router, data.router, alerts.router, health_impact.router, source_attribution.router, live.router]:
    app.include_router(r)

_LANDING = (Path(__file__).resolve().parent.parent / "web" / "index.html").read_text(encoding="utf-8")


@app.get("/", include_in_schema=False)
def root(request: Request):
    # Browsers get the landing page (live map, rankings, module guide, links to /docs).
    # API clients (curl, scripts) still get the JSON status below.
    if "text/html" in request.headers.get("accept", ""):
        return HTMLResponse(_LANDING)
    return {
        "name": "India Air Pollution Intelligence API",
        "version": "5.0.0",
        "status": "operational",
        "docs": "/docs",
        "live_data": "/live/stations  (real CPCB station data via data.gov.in)",
        "modules": [
            "monitoring","emissions","AQI","forecasting","anomaly detection",
            "GIS","source attribution","policy simulation","policy optimization",
            "MSME","health impact","economic impact","alerts","analytics","authentication","live CPCB data"
        ]
    }
