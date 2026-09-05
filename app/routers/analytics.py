from fastapi import APIRouter
from pathlib import Path
import pandas as pd

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"]
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


@router.get("/dashboard")
def dashboard():
    df = load_data()

    if df is None:
        return {
            "status": "dataset_not_available"
        }

    return {
        "status": "success",
        "dataset_records": len(df),
        "dataset_status": "synthetic development dataset",

        "pollution_summary": {
            "PM2.5_mean": round(float(df["PM25_ug_m3"].mean()), 2),
            "PM2.5_max": round(float(df["PM25_ug_m3"].max()), 2),
            "PM10_mean": round(float(df["PM10_ug_m3"].mean()), 2),
            "PM10_max": round(float(df["PM10_ug_m3"].max()), 2),
            "NO2_mean": round(float(df["NO2_ug_m3"].mean()), 2),
            "SO2_mean": round(float(df["SO2_ug_m3"].mean()), 2),
            "O3_mean": round(float(df["O3_ug_m3"].mean()), 2),
            "CO_mean": round(float(df["CO_mg_m3"].mean()), 2)
        },

        "coverage": {
            "states_ut": int(df["state_ut"].nunique()),
            "districts": int(df["district"].nunique()),
            "cities": int(df["city_ulb"].nunique()),
            "stations": int(df["station_id"].nunique()),
            "source_sectors": int(df["source_sector"].nunique())
        },

        "top_polluted_cities": (
            df.groupby("city_ulb")["PM25_ug_m3"]
            .mean()
            .sort_values(ascending=False)
            .head(10)
            .round(2)
            .to_dict()
        ),

        "source_sector_average_PM25": (
            df.groupby("source_sector")["PM25_ug_m3"]
            .mean()
            .sort_values(ascending=False)
            .round(2)
            .to_dict()
        )
    }


@router.get("/rankings")
def rankings():
    df = load_data()

    if df is None:
        return {
            "status": "dataset_not_available"
        }

    city_ranking = (
        df.groupby("city_ulb")["PM25_ug_m3"]
        .mean()
        .sort_values(ascending=False)
        .head(10)
        .round(2)
        .to_dict()
    )

    state_ranking = (
        df.groupby("state_ut")["PM25_ug_m3"]
        .mean()
        .sort_values(ascending=False)
        .head(10)
        .round(2)
        .to_dict()
    )

    station_ranking = (
        df.groupby("station_id")["PM25_ug_m3"]
        .mean()
        .sort_values(ascending=False)
        .head(10)
        .round(2)
        .to_dict()
    )

    return {
        "status": "success",
        "dataset_records": len(df),
        "ranking_metric": "average PM2.5",

        "city_ranking": city_ranking,
        "state_ut_ranking": state_ranking,
        "station_ranking": station_ranking
    }


@router.get("/trends")
def trends():
    df = load_data()

    if df is None:
        return {
            "status": "dataset_not_available"
        }

    df["timestamp_utc"] = pd.to_datetime(
        df["timestamp_utc"],
        errors="coerce"
    )

    df = df.dropna(subset=["timestamp_utc"])

    daily = (
        df.set_index("timestamp_utc")["PM25_ug_m3"]
        .resample("D")
        .mean()
        .dropna()
        .round(2)
    )

    monthly = (
        df.set_index("timestamp_utc")["PM25_ug_m3"]
        .resample("ME")
        .mean()
        .dropna()
        .round(2)
    )

    return {
        "status": "success",
        "dataset_records": len(df),
        "metric": "average PM2.5",

        "daily_trend": {
            str(index.date()): float(value)
            for index, value in daily.tail(30).items()
        },

        "monthly_trend": {
            str(index.date()): float(value)
            for index, value in monthly.items()
        }
    }
