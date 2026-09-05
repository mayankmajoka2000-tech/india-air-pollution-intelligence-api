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

    # Normalize PM2.5 between 0 and 100.
    # Higher PM2.5 = higher pollution exposure.
    min_pm25 = station_data["average_PM25"].min()
    max_pm25 = station_data["average_PM25"].max()

    if max_pm25 == min_pm25:
        station_data["pollution_exposure_score"] = 0
    else:
        station_data["pollution_exposure_score"] = (
            (
                station_data["average_PM25"] - min_pm25
            )
            / (max_pm25 - min_pm25)
            * 100
        )

    # Classify exposure level.
    def exposure_level(score):
        if score >= 75:
            return "Very High"
        elif score >= 50:
            return "High"
        elif score >= 25:
            return "Moderate"
        else:
            return "Low"

    station_data["exposure_level"] = (
        station_data["pollution_exposure_score"]
        .apply(exposure_level)
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
                "observations": int(row["observations"]),
                "pollution_exposure_score": round(
                    float(row["pollution_exposure_score"]), 2
                ),
                "exposure_level": row["exposure_level"]
            }
        })

    level_counts = (
        station_data["exposure_level"]
        .value_counts()
        .to_dict()
    )

    return {
        "status": "success",
        "dataset_records": len(df),
        "station_count": int(len(station_data)),
        "index_name": "PM2.5 Pollution Exposure Screening Index",
        "index_range": "0-100",
        "higher_score_means": "higher pollution exposure",
        "exposure_level_counts": {
            str(k): int(v)
            for k, v in level_counts.items()
        },
        "geojson": {
            "type": "FeatureCollection",
            "features": features
        },
        "available_layers": [
            "pollution",
            "station_locations"
        ],
        "future_layers": [
            "population",
            "schools",
            "hospitals",
            "roads",
            "industrial areas"
        ],
        "method": (
            "Min-max normalization of station-level average "
            "PM2.5 to a 0-100 pollution exposure screening score"
        ),
        "interpretation_note": (
            "This is a pollution-based exposure screening index "
            "derived from the synthetic development dataset. "
            "It does not represent population exposure or health "
            "risk because population, demographic, school, hospital "
            "and other vulnerability layers are not currently "
            "integrated."
        )
    }
