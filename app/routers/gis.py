from fastapi import APIRouter
from pathlib import Path
import pandas as pd

router = APIRouter(
    prefix="/gis",
    tags=["GIS"]
)

DATA_PATH = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "india_air_quality_total_320000.csv"
)


def load_data():
    if not DATA_PATH.exists():
        return None
    return pd.read_csv(DATA_PATH)


@router.get("/hotspots")
def hotspots():
    df = load_data()

    if df is None:
        return {
            "status": "dataset_not_available"
        }

    required_columns = [
        "latitude",
        "longitude",
        "PM25_ug_m3",
        "city_ulb",
        "state_ut",
        "station_id"
    ]

    missing = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing:
        return {
            "status": "required_columns_missing",
            "missing_columns": missing
        }

    df = df.dropna(
        subset=[
            "station_id",
            "latitude",
            "longitude",
            "PM25_ug_m3"
        ]
    )

    station_data = (
        df.groupby("station_id", as_index=False)
        .agg(
            city_ulb=("city_ulb", "first"),
            state_ut=("state_ut", "first"),
            latitude=("latitude", "mean"),
            longitude=("longitude", "mean"),
            average_PM25=("PM25_ug_m3", "mean"),
            observations=("PM25_ug_m3", "count")
        )
    )

    threshold = station_data["average_PM25"].quantile(0.90)

    hotspots_df = station_data[
        station_data["average_PM25"] >= threshold
    ].copy()

    hotspots_df = hotspots_df.sort_values(
        "average_PM25",
        ascending=False
    ).head(50)

    features = []

    for _, row in hotspots_df.iterrows():
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [
                    round(float(row["longitude"]), 6),
                    round(float(row["latitude"]), 6)
                ]
            },
            "properties": {
                "station_id": row["station_id"],
                "city": row["city_ulb"],
                "state_ut": row["state_ut"],
                "average_PM25": round(
                    float(row["average_PM25"]), 2
                ),
                "observations": int(row["observations"]),
                "hotspot_threshold": round(
                    float(threshold), 2
                )
            }
        })

    return {
        "status": "success",
        "dataset_records": len(df),
        "station_count": int(len(station_data)),
        "hotspot_count": int(len(features)),
        "hotspot_threshold_PM25": round(
            float(threshold), 2
        ),
        "method": (
            "station-level PM2.5 90th percentile "
            "hotspot detection"
        ),
        "geojson": {
            "type": "FeatureCollection",
            "features": features
        },
        "interpretation_note": (
            "Hotspots are identified descriptively using "
            "the 90th percentile of station-level average "
            "PM2.5 in the synthetic development dataset. "
            "This is not a formal Getis-Ord Gi*, DBSCAN, "
            "or KDE statistical hotspot analysis."
        )
    }


@router.get("/stations")
def stations():
    df = load_data()

    if df is None:
        return {
            "status": "dataset_not_available"
        }

    required_columns = [
        "station_id",
        "city_ulb",
        "state_ut",
        "latitude",
        "longitude",
        "PM25_ug_m3"
    ]

    missing = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing:
        return {
            "status": "required_columns_missing",
            "missing_columns": missing
        }

    df = df.dropna(
        subset=[
            "station_id",
            "latitude",
            "longitude",
            "PM25_ug_m3"
        ]
    )

    station_data = (
        df.groupby("station_id", as_index=False)
        .agg(
            city_ulb=("city_ulb", "first"),
            state_ut=("state_ut", "first"),
            latitude=("latitude", "mean"),
            longitude=("longitude", "mean"),
            average_PM25=("PM25_ug_m3", "mean"),
            observations=("PM25_ug_m3", "count")
        )
    )

    features = []

    for _, row in station_data.iterrows():
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [
                    round(float(row["longitude"]), 6),
                    round(float(row["latitude"]), 6)
                ]
            },
            "properties": {
                "station_id": row["station_id"],
                "city": row["city_ulb"],
                "state_ut": row["state_ut"],
                "average_PM25": round(
                    float(row["average_PM25"]), 2
                ),
                "observations": int(row["observations"])
            }
        })

    return {
        "status": "success",
        "dataset_records": len(df),
        "station_count": int(len(station_data)),
        "method": (
            "station-level aggregation of average PM2.5 "
            "from the synthetic development dataset"
        ),
        "geojson": {
            "type": "FeatureCollection",
            "features": features
        },
        "interpretation_note": (
            "Station locations and pollution values are "
            "derived from the synthetic development dataset "
            "and should not be interpreted as official CPCB "
            "station observations."
        )
    }


@router.get("/exposure")
def exposure():
    return {
        "layers": [
            "population",
            "pollution",
            "schools",
            "hospitals",
            "roads",
            "industrial areas"
        ],
        "output": "spatial exposure index"
    }
