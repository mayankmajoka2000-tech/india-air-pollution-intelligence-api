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


def calculate_emissions(x: MSME):
    fuel_co2e = x.fuel_consumption * 2.75
    electricity_co2e = x.electricity_kwh * 0.70

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

    # Environmental performance score
    # Lower emissions and lower intensity
    # produce a higher score.
    emission_score = max(
        0,
        100 - (total / 10000)
    )

    intensity_score = max(
        0,
        100 - (intensity * 10)
    )

    # Combined screening score
    screening_score = (
        emission_score * 0.60
        + intensity_score * 0.40
    )

    screening_score = min(
        100,
        max(0, screening_score)
    )

    if screening_score >= 75:
        eligibility = "High potential"
    elif screening_score >= 50:
        eligibility = "Moderate potential"
    elif screening_score >= 25:
        eligibility = "Low potential"
    else:
        eligibility = "Requires improvement"

    # Identify the dominant energy source
    if (
        emissions["fuel_co2e"]
        > emissions["electricity_co2e"]
    ):
        dominant_source = "fuel consumption"
    elif (
        emissions["electricity_co2e"]
        > emissions["fuel_co2e"]
    ):
        dominant_source = "electricity consumption"
    else:
        dominant_source = "balanced"

    recommended_actions = []

    if emissions["fuel_co2e"] > 0:
        recommended_actions.append(
            "clean fuel transition"
        )

    if emissions["electricity_co2e"] > 0:
        recommended_actions.append(
            "energy efficiency and renewable electricity"
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
        "dominant_emission_source": dominant_source,
        "emission_score": round(
            emission_score,
            2
        ),
        "intensity_score": round(
            intensity_score,
            2
        ),
        "screening_score": round(
            screening_score,
            2
        ),
        "green_finance_potential": eligibility,
        "recommended_actions": recommended_actions,
        "scoring_weights": {
            "absolute_emissions": 0.60,
            "emission_intensity": 0.40
        },
        "method": (
            "Screening score combining absolute "
            "estimated CO2e and emission intensity"
        ),
        "important_note": (
            "This is a preliminary screening tool, "
            "not a formal lending or green-finance "
            "eligibility decision. Actual financing "
            "decisions should use verified emissions, "
            "sector benchmarks, project additionality, "
            "credit risk, financial viability and "
            "applicable lender or regulatory criteria."
        )
    }
