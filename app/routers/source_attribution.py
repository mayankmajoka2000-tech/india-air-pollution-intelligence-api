from fastapi import APIRouter
from pydantic import BaseModel
from pathlib import Path
import pandas as pd

router = APIRouter(
    prefix="/source-attribution",
    tags=["Source Attribution"]
)

DATA_PATH = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "india_air_quality_total_320000.csv"
)


class Contributions(BaseModel):
    transport: float = 0
    industry: float = 0
    power: float = 0
    construction: float = 0
    road_dust: float = 0
    waste: float = 0
    agriculture: float = 0
    residential: float = 0


def load_data():
    if not DATA_PATH.exists():
        return None
    return pd.read_csv(DATA_PATH)


@router.post("/normalize")
def normalize(x: Contributions):
    d = x.model_dump()
    total = sum(d.values())

    return {
        "total": total,
        "shares": {
            k: round((v / total * 100), 2) if total else 0
            for k, v in d.items()
        },
        "method": "input contribution normalization"
    }


@router.post("/scenario")
def scenario(x: Contributions):
    d = x.model_dump()
    total = sum(d.values())

    return {
        "baseline": d,
        "total": total,
        "top_source": max(d, key=d.get) if total else None
    }


@router.get("/data-driven")
def data_driven():
    df = load_data()

    if df is None:
        return {
            "status": "dataset_not_available"
        }

    if "source_sector" not in df.columns or "PM25_ug_m3" not in df.columns:
        return {
            "status": "required_columns_not_available"
        }

    sector_pm25 = (
        df.groupby("source_sector")["PM25_ug_m3"]
        .mean()
        .sort_values(ascending=False)
    )

    total = sector_pm25.sum()

    shares = (
        sector_pm25 / total * 100
        if total
        else sector_pm25 * 0
    )

    return {
        "status": "success",
        "dataset_records": len(df),
        "metric": "average PM2.5 by source sector",
        "sector_average_PM25": {
            k: round(float(v), 2)
            for k, v in sector_pm25.items()
        },
        "relative_share_of_sector_average": {
            k: round(float(v), 2)
            for k, v in shares.items()
        },
        "top_source_sector": (
            str(sector_pm25.index[0])
            if len(sector_pm25) > 0
            else None
        ),
        "method": (
            "dataset-driven grouping of average PM2.5 "
            "by source_sector"
        ),
        "interpretation_note": (
            "These are descriptive sector-level averages "
            "from the synthetic development dataset and "
            "should not be interpreted as causal emission "
            "source apportionment."
        )
    }
