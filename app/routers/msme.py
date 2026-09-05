from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter(
    prefix="/msme",
    tags=["MSME"]
)


class MSME(BaseModel):
    sector: str
    fuel_consumption: float = Field(ge=0)
    electricity_kwh: float = Field(ge=0)
    annual_output: float = Field(gt=0)


# Screening-level sector benchmarks.
# These are development benchmarks for API screening,
# not official regulatory thresholds.
SECTOR_BENCHMARKS = {
    "manufacturing": {
        "emission_intensity": 2.0
    },
    "textile": {
        "emission_intensity": 1.8
    },
    "food processing": {
        "emission_intensity": 1.5
    },
    "chemical": {
        "emission_intensity": 2.5
    },
    "cement": {
        "emission_intensity": 3.0
    },
    "metal": {
        "emission_intensity": 2.8
    },
    "automotive": {
        "emission_intensity": 2.2
    },
    "pharmaceutical": {
        "emission_intensity": 1.6
    },
    "default": {
        "emission_intensity": 2.0
    }
}


def calculate_emissions(x: MSME):

    fuel_co2e = (
        x.fuel_consumption * 2.75
    )

    electricity_co2e = (
        x.electricity_kwh * 0.70
    )

    total_co2e = (
        fuel_co2e
        + electricity_co2e
    )

    intensity = (
        total_co2e
        / x.annual_output
    )

    return {
        "fuel_co2e": fuel_co2e,
        "electricity_co2e": electricity_co2e,
        "total_co2e": total_co2e,
        "intensity": intensity
    }


def get_sector_benchmark(sector: str):

    sector_key = sector.strip().lower()

    benchmark = SECTOR_BENCHMARKS.get(
        sector_key,
        SECTOR_BENCHMARKS["default"]
    )

    benchmark_source = (
        "sector-specific development benchmark"
        if sector_key in SECTOR_BENCHMARKS
        else "default development benchmark"
    )

    return (
        benchmark["emission_intensity"],
        benchmark_source
    )


@router.post("/assessment")
def assessment(x: MSME):

    emissions = calculate_emissions(x)

    total = emissions["total_co2e"]

    return {
        "status": "success",
        "sector": x.sector,
        "estimated_co2e": round(
            total,
            2
        ),
        "emission_intensity": round(
            emissions["intensity"],
            4
        ),
        "fuel_co2e": round(
            emissions["fuel_co2e"],
            2
        ),
        "electricity_co2e": round(
            emissions["electricity_co2e"],
            2
        ),
        "priority": (
            "High"
            if total > 100000
            else "Standard"
        ),
        "method": (
            "Estimated CO2e from fuel consumption "
            "and electricity consumption"
        ),
        "interpretation_note": (
            "This is a screening-level estimate "
            "based on the emission factors supplied "
            "to the model. It is not a verified "
            "greenhouse-gas inventory."
        )
    }


@router.post("/green-finance-screening")
def finance(x: MSME):

    emissions = calculate_emissions(x)

    total = emissions["total_co2e"]
    intensity = emissions["intensity"]

    # ------------------------------------------------
    # 1. Absolute emission score
    # ------------------------------------------------

    emission_score = max(
        0,
        100 - (total / 10000)
    )

    # ------------------------------------------------
    # 2. General intensity score
    # ------------------------------------------------

    intensity_score = max(
        0,
        100 - (intensity * 10)
    )

    # ------------------------------------------------
    # 3. Sector benchmark comparison
    # ------------------------------------------------

    benchmark, benchmark_source = (
        get_sector_benchmark(x.sector)
    )

    benchmark_ratio = (
        intensity / benchmark
        if benchmark > 0
        else None
    )

    if benchmark_ratio is not None:

        if benchmark_ratio <= 0.75:
            benchmark_performance = "Better than benchmark"

        elif benchmark_ratio <= 1.00:
            benchmark_performance = "Near benchmark"

        elif benchmark_ratio <= 1.25:
            benchmark_performance = "Above benchmark"

        else:
            benchmark_performance = (
                "Significantly above benchmark"
            )

    else:
        benchmark_performance = (
            "Benchmark unavailable"
        )

    # Benchmark score:
    # 100 means performance is at or below
    # 75% of the benchmark.
    if benchmark_ratio is not None:

        benchmark_score = max(
            0,
            min(
                100,
                100 - (
                    (benchmark_ratio - 0.75)
                    * 100
                )
            )
        )

    else:
        benchmark_score = 50

    # ------------------------------------------------
    # 4. Combined green-finance screening score
    # ------------------------------------------------

    screening_score = (
        emission_score * 0.40
        + intensity_score * 0.25
        + benchmark_score * 0.35
    )

    screening_score = min(
        100,
        max(
            0,
            screening_score
        )
    )

    # ------------------------------------------------
    # 5. Finance potential
    # ------------------------------------------------

    if screening_score >= 75:
        eligibility = "High potential"

    elif screening_score >= 50:
        eligibility = "Moderate potential"

    elif screening_score >= 25:
        eligibility = "Low potential"

    else:
        eligibility = "Requires improvement"

    # ------------------------------------------------
    # 6. Dominant emission source
    # ------------------------------------------------

    if (
        emissions["fuel_co2e"]
        > emissions["electricity_co2e"]
    ):
        dominant_source = (
            "fuel consumption"
        )

    elif (
        emissions["electricity_co2e"]
        > emissions["fuel_co2e"]
    ):
        dominant_source = (
            "electricity consumption"
        )

    else:
        dominant_source = "balanced"

    # ------------------------------------------------
    # 7. Recommended transition actions
    # ------------------------------------------------

    recommended_actions = []

    if emissions["fuel_co2e"] > 0:
        recommended_actions.append(
            "clean fuel transition"
        )

    if emissions["electricity_co2e"] > 0:
        recommended_actions.append(
            "energy efficiency and renewable electricity"
        )

    if benchmark_ratio is not None:

        if benchmark_ratio > 1:
            recommended_actions.append(
                "sector-specific emission intensity reduction"
            )

        if benchmark_ratio > 1.25:
            recommended_actions.append(
                "prepare an emissions-reduction investment plan"
            )

    recommended_actions.extend([
        "emission monitoring",
        "pollution-control equipment",
        "resource efficiency"
    ])

    return {
        "status": "success",
        "sector": x.sector,

        "estimated_co2e": round(
            total,
            2
        ),

        "emission_intensity": round(
            intensity,
            4
        ),

        "fuel_co2e": round(
            emissions["fuel_co2e"],
            2
        ),

        "electricity_co2e": round(
            emissions["electricity_co2e"],
            2
        ),

        "dominant_emission_source": (
            dominant_source
        ),

        "sector_benchmark": round(
            benchmark,
            4
        ),

        "benchmark_ratio": round(
            benchmark_ratio,
            4
        )
        if benchmark_ratio is not None
        else None,

        "benchmark_performance": (
            benchmark_performance
        ),

        "benchmark_source": (
            benchmark_source
        ),

        "emission_score": round(
            emission_score,
            2
        ),

        "intensity_score": round(
            intensity_score,
            2
        ),

        "benchmark_score": round(
            benchmark_score,
            2
        ),

        "screening_score": round(
            screening_score,
            2
        ),

        "green_finance_potential": (
            eligibility
        ),

        "recommended_actions": (
            recommended_actions
        ),

        "scoring_weights": {
            "absolute_emissions": 0.40,
            "emission_intensity": 0.25,
            "sector_benchmark": 0.35
        },

        "method": (
            "Green-finance screening using absolute "
            "emissions, emission intensity and "
            "sector benchmark performance"
        ),

        "important_note": (
            "Sector benchmarks in this API are "
            "development-stage screening assumptions "
            "and are not official regulatory or "
            "lending thresholds. Actual green-finance "
            "decisions should use verified emissions, "
            "sector-specific benchmarks, project "
            "additionality, financial viability, "
            "credit risk and applicable lender or "
            "regulatory criteria."
        )
    }
