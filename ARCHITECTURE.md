# Ultimate Architecture
Client/Dashboard -> FastAPI -> Auth/Rate Limit -> Analytics/ML/GIS/Policy Services
                         |-> PostgreSQL/PostGIS/TimescaleDB
                         |-> Redis/Celery
                         |-> Verified data ingestion (CPCB/PRANA/OpenAQ/other licensed sources)
                         |-> ML model registry
