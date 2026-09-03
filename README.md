# India Air Pollution Intelligence API

🚀 **Live API:** https://india-air-pollution-intelligence-api.onrender.com

📚 **Interactive Swagger Documentation:** https://india-air-pollution-intelligence-api.onrender.com/docs

❤️ **Health Check:** https://india-air-pollution-intelligence-api.onrender.com/health

📊 **Dataset:** 320,000 synthetic India-level air-quality records
# India Air Pollution Intelligence API — ULTIMATE v5.0

## Run
pip install -r requirements.txt
uvicorn app.main:app --reload

Swagger: http://127.0.0.1:8000/docs

## Docker
docker compose up --build

## Dataset
`data/india_air_quality_total_320000.csv` contains 320,000 synthetic development records.
They are NOT official CPCB measurements. For production analytics, ingest verified observations
and preserve source, station, timestamp, QC and licensing provenance.

## Core modules
- India hierarchy
- Air-quality monitoring
- Emission calculation and scenarios
- AQI
- Forecasting and ML model catalog
- Anomaly detection
- GIS/hotspots/exposure
- Source attribution
- Policy simulation and optimization
- MSME/green-finance screening
- Health/economic screening
- Alerts
- Rankings/trends/dashboard endpoints
- PostgreSQL/PostGIS schema
- Redis/Celery architecture
- Authentication scaffold
- Docker and tests

## Production note
Some advanced components are deliberately scaffolds rather than claims of trained/validated
production models. Replace them with verified data, official CPCB breakpoint tables,
validated source-apportionment models, trained forecasting models, secure JWT/OAuth2,
rate limiting, observability and deployment secrets before real-world use.
