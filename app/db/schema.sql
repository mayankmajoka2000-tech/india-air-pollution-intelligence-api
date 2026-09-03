CREATE EXTENSION IF NOT EXISTS postgis;
CREATE TABLE IF NOT EXISTS air_observations (
    id BIGSERIAL PRIMARY KEY,
    timestamp_utc TIMESTAMPTZ NOT NULL,
    state_ut TEXT, district TEXT, city_ulb TEXT, station_id TEXT,
    latitude DOUBLE PRECISION, longitude DOUBLE PRECISION,
    source_sector TEXT,
    pm25 DOUBLE PRECISION, pm10 DOUBLE PRECISION, no2 DOUBLE PRECISION,
    so2 DOUBLE PRECISION, co DOUBLE PRECISION, o3 DOUBLE PRECISION,
    nh3 DOUBLE PRECISION, pb DOUBLE PRECISION,
    temperature_c DOUBLE PRECISION, relative_humidity_pct DOUBLE PRECISION,
    wind_speed_m_s DOUBLE PRECISION, wind_direction_deg DOUBLE PRECISION,
    rainfall_mm DOUBLE PRECISION, pressure_hpa DOUBLE PRECISION,
    data_status TEXT,
    geom geometry(Point,4326)
);
CREATE INDEX IF NOT EXISTS idx_air_time ON air_observations(timestamp_utc);
CREATE INDEX IF NOT EXISTS idx_air_geom ON air_observations USING GIST(geom);
