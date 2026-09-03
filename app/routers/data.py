from fastapi import APIRouter, Query
from pathlib import Path
import pandas as pd
from urllib.request import urlretrieve

router = APIRouter(prefix="/data", tags=["Data"])

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
PATH = DATA_DIR / "india_air_quality_total_320000.csv"

DATASET_URL = (
    "https://github.com/"
    "mayankmajoka2000-tech/"
    "india-air-pollution-intelligence-api/"
    "releases/download/v5.0.0-data/"
    "india_air_quality_total_320000.csv"
)


def ensure_dataset():
    """Download the 320,000-record dataset if it is not available locally."""
    if PATH.exists() and PATH.stat().st_size > 0:
        return True

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    try:
        urlretrieve(DATASET_URL, PATH)
        return PATH.exists() and PATH.stat().st_size > 0
    except Exception:
        if PATH.exists():
            PATH.unlink()
        return False


@router.get("/info")
def info():
    if not ensure_dataset():
        return {
            "available": False,
            "records": 0,
            "status": "dataset unavailable"
        }

    cols = pd.read_csv(PATH, nrows=1).columns.tolist()

    return {
        "available": True,
        "records": 320000,
        "columns": cols,
        "status": "synthetic development dataset"
    }


@router.get("/sample")
def sample(limit: int = Query(20, ge=1, le=1000)):
    if not ensure_dataset():
        return {
            "available": False,
            "records": 0,
            "status": "dataset unavailable"
        }

    return pd.read_csv(
        PATH,
        nrows=limit
    ).to_dict(orient="records")
