from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import health, india, emissions, aqi, monitoring, forecast, policy, msme, analytics, gis, auth, data, alerts, health_impact, source_attribution

app = FastAPI(
    title="India Air Pollution Intelligence API — ULTIMATE",
    version="5.0.0",
    description="India-scale air pollution intelligence platform covering monitoring, emissions, AQI, forecasting, GIS, source attribution, policy, MSMEs, health/economic impacts, alerts and ML."
)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

for r in [health.router, india.router, emissions.router, aqi.router, monitoring.router,
          forecast.router, policy.router, msme.router, analytics.router, gis.router,
          auth.router, data.router, alerts.router, health_impact.router, source_attribution.router]:
    app.include_router(r)

@app.get("/")
def root():
    return {
        "name": "India Air Pollution Intelligence API",
        "version": "5.0.0",
        "status": "operational",
        "docs": "/docs",
        "modules": [
            "monitoring","emissions","AQI","forecasting","anomaly detection",
            "GIS","source attribution","policy simulation","policy optimization",
            "MSME","health impact","economic impact","alerts","analytics","authentication"
        ]
    }
