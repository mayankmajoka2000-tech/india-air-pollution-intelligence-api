# India Air Pollution Intelligence API

🚀 **Live API:** https://india-air-pollution-intelligence-api.onrender.com

📚 **Interactive Swagger Documentation:** https://india-air-pollution-intelligence-api.onrender.com/docs

❤️ **Health Check:** https://india-air-pollution-intelligence-api.onrender.com/health

📊 **Data:** live CPCB station readings via data.gov.in (`/live/*`) + a 320,000-record synthetic development dataset (`/data/*`)

## Live CPCB data (real observations)

The `/live` endpoints pull **real-time readings from CPCB's continuous ambient air quality
monitoring stations** through the Open Government Data Platform India
([data.gov.in resource 3b01bcb8-0b14-4abf-b6f2-c1bfd384ba69](https://data.gov.in/resource/real-time-air-quality-index-various-locations),
GODL licence), and compute AQI with the **official CPCB National AQI breakpoints**.

| Endpoint | What it returns |
|---|---|
| `GET /live/status` | Feed connection check, row counts, source and licence |
| `GET /live/readings?state=&city=&pollutant=` | Raw pollutant readings (24-h min / max / avg) per station |
| `GET /live/stations?state=&city=` | Station AQI, category and prominent pollutant, ranked worst-first |
| `GET /live/cities?state=` | City ranking: mean / max station AQI and worst station |
| `POST /aqi/calculate` | AQI from concentrations using CPCB breakpoints and the 3-pollutant rule |
| `GET /aqi/breakpoints` | The CPCB breakpoint table |

**Setup:** register free at [data.gov.in](https://data.gov.in), copy your API key, and set it as an
environment variable (on Render: *Environment → Add Environment Variable*):

```
DATA_GOV_IN_API_KEY=your_key_here
```

**Hosting note:** data.gov.in refuses connections from servers outside India (tested from Render's Oregon and
Singapore regions). When the live feed can't be reached, `/live/*` serves the saved snapshot in
`data/cpcb_snapshot.json` and says so (`"mode": "snapshot"`, `snapshot_as_of`). Refresh it from a machine in India:
`DATA_GOV_IN_API_KEY=... python scripts/refresh_cpcb_snapshot.py`, or from the CSV on the data.gov.in resource page:
`python scripts/refresh_cpcb_snapshot.py --from-csv file.csv`.

Without a key the API falls back to data.gov.in's public sample key, which returns only 10 rows.
Responses are cached for 15 minutes (`CPCB_CACHE_SECONDS`). If data.gov.in is down the endpoints
return HTTP 503 with the reason; they never fall back to synthetic data.

Every response carries `source`, `fetched_at` and `using_sample_key` fields so the provenance of each
number is explicit.

# India Air Pollution Intelligence API — ULTIMATE v5.0

## Run
pip install -r requirements.txt
uvicorn app.main:app --reload

Swagger: http://127.0.0.1:8000/docs

## Docker
docker compose up --build

## Synthetic development dataset
`data/india_air_quality_total_320000.csv` contains 320,000 synthetic development records, used by
the `/data`, forecasting and ML-training modules.
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
