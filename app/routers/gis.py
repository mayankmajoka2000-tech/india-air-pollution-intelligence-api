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
            "latitude",
            "longitude",
            "PM25_ug_m3"
        ]
    )

    # Aggregate pollution at station level
    station_data = (
        df.groupby(
            [
                "station_id",
                "city_ulb",
                "state_ut",
                "latitude",
                "longitude"
            ],
            as_index=False
        )["PM25_ug_m3"]
        .mean()
    )

    # Define hotspot threshold as the 90th percentile
    threshold = station_data["PM25_ug_m3"].quantile(0.90)

    hotspots_df = station_data[
        station_data["PM25_ug_m3"] >= threshold
    ].copy()

    hotspots_df = hotspots_df.sort_values(
        "PM25_ug_m3",
        ascending=False
    ).head(50)

    features = []

    for _, row in hotspots_df.iterrows():
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [
                    float(row["longitude"]),
                    float(row["latitude"])
                ]
            },
            "properties": {
                "station_id": row["station_id"],
                "city": row["city_ulb"],
                "state_ut": row["state_ut"],
                "average_PM25": round(
                    float(row["PM25_ug_m3"]), 2
                ),
                "hotspot_threshold": round(
                    float(threshold), 2
                )
            }
        })

    return {
        "status": "success",
        "dataset_records": len(df),
        "station_count": len(station_data),
        "hotspot_count": len(features),
        "method": "station-level PM2.5 90th percentile hotspot detection",
        "geojson": {
            "type": "FeatureCollection",
            "features": features
        },
        "interpretation_note": (
            "Hotspots are identified descriptively using the "
            "90th percentile of station-level average PM2.5 "
            "in the synthetic development dataset. "
            "This is not a formal Getis-Ord Gi*, DBSCAN, or KDE "
            "statistical hotspot analysis."
        )
    }


@router.get("/stations")
def stations():
    return {
        "output": "GeoJSON-ready station layer"
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
